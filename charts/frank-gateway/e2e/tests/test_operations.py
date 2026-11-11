"""Operations on a real cluster: shutdown and rolling updates, the Control API, metrics, diagnostic mode and upgrades."""
import json
import threading
import time

import pytest
import yaml

from fge2e import apisix, net
from fge2e.chart import merge
from fge2e.tools import kubectl, wait_until

HTTP = {"port": 80, "tls": False}


def load_balanced(deployer, **overrides):
    values = merge(
        deployer.base_values(),
        merge({"service": {"type": "LoadBalancer"}, "topologySpreadConstraints": []}, overrides),
    )
    release = deployer.deploy(values=values)
    address = release.service_address()
    wait_until(lambda: net.request(address, path="/echo", **HTTP).ok, 60, message="the gateway on its external address")
    return release, address


def test_an_in_flight_request_survives_the_deletion_of_the_pod(deployer):
    """The pod keeps serving while it is removed from the endpoints, and a request that is still running finishes."""
    release, address = load_balanced(deployer, replicas=1)
    try:
        result = {}

        def slow_request():
            started = time.monotonic()
            result["response"] = net.request(address, path="/slow-long", timeout=60, **HTTP)
            result["seconds"] = time.monotonic() - started

        thread = threading.Thread(target=slow_request)
        thread.start()
        time.sleep(2)
        old = release.pods()[0]["metadata"]["name"]
        release.kubectl("delete", "pod", old, "--wait=false")
        thread.join(90)

        response = result["response"]
        assert response.ok, f"the request was dropped: {response}"
        assert response.text == "slow-long"
        assert result["seconds"] >= 19, "the answer was not delayed, so the test did not test a shutdown"
        wait_until(lambda: old not in [p["metadata"]["name"] for p in release.pods()], 90, message="the old pod to be gone")
    finally:
        deployer.remove(release)


def test_a_rolling_update_drops_no_requests(deployer):
    release, address = load_balanced(deployer, replicas=2)
    try:
        results, stop = [], threading.Event()

        def load():
            while not stop.is_set():
                response = net.request(address, path="/echo", timeout=5, **HTTP)
                results.append(response.status if response.error is None else response.error)
                time.sleep(0.05)

        thread = threading.Thread(target=load)
        thread.start()
        time.sleep(3)
        before = {p["metadata"]["name"] for p in release.pods()}
        release.upgrade({"standalone": {"apisixYaml": apisix.apisix_yaml() + "\n# a new version\n"}})
        wait_until(
            lambda: len(release.pods()) == 2 and not before & {p["metadata"]["name"] for p in release.pods()},
            180, message="all pods to be replaced",
        )
        time.sleep(3)
        stop.set()
        thread.join(30)

        failures = [r for r in results if r != 200]
        assert len(results) > 100, f"too few requests ({len(results)}) to say anything"
        assert not failures, f"{len(failures)} of {len(results)} requests failed during the update: {failures[:5]}"
    finally:
        deployer.remove(release)


def allow_from(namespace):
    return [{"namespaceSelector": {"matchLabels": {"kubernetes.io/metadata.name": namespace}}}]


def test_the_control_api_is_only_reachable_from_the_allowed_peers(deployer):
    release = deployer.deploy(
        values=merge(
            deployer.base_values(),
            {
                "control": {"enabled": True},
                "networkPolicy": {"enabled": True, "control": {"from": allow_from("e2e-dashboard")}},
            },
        )
    )
    try:
        allowed = deployer.client_pod("e2e-dashboard")
        denied = deployer.client_pod("e2e-intruder")
        control = f"http://{release.fullname}-control.{release.namespace}.svc:9090/v1/healthcheck"
        gateway = f"http://{release.fullname}.{release.namespace}.svc/echo"

        wait_until(
            lambda: allowed.get(control).returncode == 0, 30, message="the allowed namespace to reach the Control API"
        )
        wait_until(lambda: denied.get(control, timeout=3).returncode != 0, 60, message="the Control API to be blocked")
        for name, pod in (("the allowed namespace", allowed), ("the other namespace", denied)):
            answer = pod.get(gateway)
            assert answer.returncode == 0, f"{name} cannot reach the gateway port: {answer.stderr}"
            assert json.loads(answer.stdout)["scheme"] == "http"
    finally:
        deployer.remove(release)


def test_the_control_api_is_not_exposed_by_any_exposure_method(deployer):
    release = deployer.deploy(
        values=merge(
            deployer.base_values(),
            {
                "control": {"enabled": True},
                "service": {"type": "LoadBalancer"},
                "ingress": {"enabled": True, "ingressClassName": "haproxy", "rules": [{"host": "api.e2e.test", "http": {"paths": [{"path": "/"}]}}]},
            },
        )
    )
    try:
        services = json.loads(release.kubectl("get", "services", "-o", "json").stdout)["items"]
        by_name = {s["metadata"]["name"]: s for s in services}
        control = by_name[f"{release.fullname}-control"]
        assert control["spec"]["type"] == "ClusterIP"
        gateway_ports = {p["port"] for p in by_name[release.fullname]["spec"]["ports"]}
        assert gateway_ports == {80, 443}, f"the gateway Service exposes {gateway_ports}"
        ingress = json.loads(release.kubectl("get", "ingress", "-o", "json").stdout)["items"][0]
        backends = [
            p["backend"]["service"] for r in ingress["spec"]["rules"] for p in r["http"]["paths"]
        ]
        assert all(b["name"] == release.fullname for b in backends), backends
        assert all(b["port"].get("name") == "https" for b in backends), backends
    finally:
        deployer.remove(release)


def test_metrics_are_served_and_the_servicemonitor_selects_the_metrics_service(deployer):
    release = deployer.deploy(
        values=merge(
            deployer.base_values(prometheus=True),
            {"metrics": {"enabled": True, "serviceMonitor": {"enabled": True, "labels": {"release": "prometheus"}}}},
        )
    )
    try:
        def request_counters():
            release.get_local("/echo")
            text = release.get_local("/apisix/prometheus/metrics", port=9091)
            return text if "apisix_http_status" in text else None

        # The counters are flushed to the exporter periodically
        metrics = wait_until(request_counters, 60, interval=3, message="the request counters in the metrics")
        assert "apisix_http_requests_total" in metrics
        assert 'route="echo"' in metrics
        monitor = json.loads(release.kubectl("get", "servicemonitor", release.fullname, "-o", "json").stdout)
        selector = monitor["spec"]["selector"]["matchLabels"]
        label_args = ",".join(f"{k}={v}" for k, v in selector.items())
        selected = json.loads(release.kubectl("get", "services", "-l", label_args, "-o", "json").stdout)["items"]
        assert [s["metadata"]["name"] for s in selected] == [f"{release.fullname}-metrics"]
        endpoints = json.loads(release.kubectl("get", "endpoints", f"{release.fullname}-metrics", "-o", "json").stdout)
        assert endpoints["subsets"][0]["addresses"], "the metrics Service has no endpoints"
        assert monitor["metadata"]["labels"]["release"] == "prometheus"
    finally:
        deployer.remove(release)


def test_diagnostic_mode_only_sleeps_and_the_gateway_can_be_started_by_hand(deployer):
    release = deployer.deploy()
    try:
        release.upgrade({"diagnosticMode": {"enabled": True}})
        release.wait_ready()
        wait_until(lambda: len(release.pods()) == 1, 120, message="a single pod")
        container = release.pods()[0]["spec"]["containers"][0]
        assert container["command"] == ["sleep"] and container["args"] == ["infinity"]
        assert "livenessProbe" not in container and "readinessProbe" not in container
        assert release.get_local("/echo") == "", "the gateway runs in diagnostic mode"

        release.exec("sh", "-c", "nohup /docker-entrypoint.sh docker-start > /tmp/gateway.log 2>&1 &")
        answer = wait_until(lambda: release.get_local("/echo") or None, 60, message="the gateway started by hand")
        assert json.loads(answer)["scheme"] == "http"
    finally:
        deployer.remove(release)


def test_upgrade_to_all_features_and_a_rollback(deployer):
    release = deployer.deploy()
    try:
        everything = {
            "control": {"enabled": True},
            "metrics": {"enabled": True, "serviceMonitor": {"enabled": True}},
            "networkPolicy": {"enabled": True},
            "podDisruptionBudget": {"enabled": True},
            "service": {"type": "LoadBalancer"},
        }
        release.upgrade(everything)
        release.wait_ready()
        names = lambda kind: {  # noqa: E731
            i["metadata"]["name"] for i in json.loads(release.kubectl("get", kind, "-o", "json").stdout)["items"]
        }
        assert f"{release.fullname}-control" in names("services")
        assert f"{release.fullname}-metrics" in names("services")
        assert release.fullname in names("networkpolicies")
        assert release.fullname in names("poddisruptionbudgets")
        assert release.fullname in names("servicemonitors")
        release.service_address()
        wait_until(lambda: json.loads(release.get_local("/echo") or "{}").get("scheme") == "http", 60, message="the gateway")

        release.rollback(1)
        release.wait_ready()
        assert f"{release.fullname}-control" not in names("services")
        assert release.fullname not in names("networkpolicies")
        wait_until(lambda: json.loads(release.get_local("/echo") or "{}").get("scheme") == "http", 60, message="the gateway")
    finally:
        deployer.remove(release)
