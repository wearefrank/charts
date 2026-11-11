"""The chart on a real cluster: the pod, the routes, reloads, shutdown, the Control API, metrics and upgrades."""
import json
import time

import pytest
import yaml

from fge2e import apisix, net
from fge2e.chart import merge
from fge2e.tools import kubectl, wait_until


@pytest.fixture(scope="module")
def core(deployer):
    release = deployer.deploy(name="core")
    yield release
    deployer.remove(release)


def test_pod_runs_with_the_baseline_security_context(core):
    """The init container, the emptyDir volumes and fsGroup work on a real kubelet, with a read-only root filesystem."""
    pod = core.pods()[0]
    assert pod["status"]["phase"] == "Running"
    pod_context = pod["spec"]["securityContext"]
    assert pod_context["runAsNonRoot"] is True
    assert pod_context["runAsUser"] == 636
    assert pod_context["seccompProfile"]["type"] == "RuntimeDefault"
    container = next(c for c in pod["spec"]["containers"] if c["name"] == "gateway")
    assert container["securityContext"]["readOnlyRootFilesystem"] is True
    assert container["securityContext"]["allowPrivilegeEscalation"] is False

    assert core.exec("id", "-u").stdout.strip() == "636"
    status = core.exec("cat", "/proc/1/status").stdout
    assert "CapEff:\t0000000000000000" in status, "the process has capabilities"
    assert "Seccomp:\t2" in status, "the seccomp filter is not active"


def test_root_filesystem_is_read_only_and_the_writable_paths_work(core):
    denied = core.exec("touch", "/usr/local/apisix/apisix/not-allowed", check=False)
    assert denied.returncode != 0
    assert "Read-only file system" in denied.stderr
    for path in ("/usr/local/apisix/conf", "/usr/local/apisix/logs", "/usr/local/apisix/client_body_temp", "/tmp"):
        assert core.exec("touch", f"{path}/e2e-write-test", check=False).returncode == 0, path


def test_apisix_yaml_is_linked_into_the_conf_directory(core):
    link = core.exec("readlink", "/usr/local/apisix/conf/apisix.yaml").stdout.strip()
    assert link == "/apisix-config/apisix.yaml"


def test_a_route_of_apisix_yaml_answers(core):
    answer = json.loads(core.get_local("/echo"))
    assert answer["scheme"] == "http"
    assert answer["pod"] == core.pods()[0]["metadata"]["name"]


def test_a_change_of_the_inline_apisix_yaml_rolls_the_pods(core):
    before = core.pods()[0]["metadata"]["name"]
    core.upgrade({"standalone": {"apisixYaml": apisix.apisix_yaml(backend=None) + "\n# changed\n"}})
    core.wait_ready()
    wait_until(lambda: core.pods()[0]["metadata"]["name"] != before and len(core.pods()) == 1, 120, message="a new pod")
    assert json.loads(core.get_local("/echo"))["scheme"] == "http"


def test_an_existing_configmap_is_reloaded_without_restarting_the_pod(deployer):
    """APISIX picks up a changed file, the pods are not restarted, so routes can change without a rollout."""
    first = yaml.safe_dump({"routes": [{"id": "one", "uri": "/one", "plugins": {"mocking": {"response_example": "one"}}}]})
    release = deployer.deploy(
        name="reload",
        values=merge(deployer.base_values(), {"standalone": {"existingConfigMap": "my-routes"}}),
        wait=False,
    )
    try:
        configmap = lambda content: yaml.safe_dump(  # noqa: E731
            {
                "apiVersion": "v1", "kind": "ConfigMap",
                "metadata": {"name": "my-routes", "namespace": release.namespace},
                "data": {"apisix.yaml": content + "#END\n"},
            }
        )
        kubectl("apply", "-f", "-", input=configmap(first))
        release.wait_ready()
        pod = release.pods()[0]["metadata"]["name"]
        wait_until(lambda: release.get_local("/one") == "one", 120, message="the first route")

        second = yaml.safe_dump({"routes": [{"id": "two", "uri": "/two", "plugins": {"mocking": {"response_example": "two"}}}]})
        kubectl("apply", "-f", "-", input=configmap(second))
        wait_until(lambda: release.get_local("/two") == "two", 180, interval=5, message="the changed route")

        assert release.pods()[0]["metadata"]["name"] == pod
        assert release.pods()[0]["status"]["containerStatuses"][0]["restartCount"] == 0
    finally:
        deployer.remove(release)
