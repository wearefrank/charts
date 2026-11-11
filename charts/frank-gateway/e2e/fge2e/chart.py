"""Installs the chart in a namespace of its own and gives the tests a handle on the release."""
import copy
import json
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional

import yaml

from . import apisix, cluster, config
from .cluster import ClusterInfo
from .pki import Pki
from .tools import apply, helm, kubectl, log, run, wait_until


NAMESPACE_LABEL = "fge2e=true"


def create_namespace(namespace: str) -> None:
    """The tests label their namespaces, so leftovers of an aborted run can be found."""
    kubectl("create", "namespace", namespace)
    kubectl("label", "namespace", namespace, NAMESPACE_LABEL)


def delete_leftover_namespaces() -> None:
    kubectl("delete", "namespace", "-l", NAMESPACE_LABEL, "--ignore-not-found", "--timeout=180s", check=False, timeout=240)


def merge(base: dict, override: dict) -> dict:
    """Deep merge, like Helm does for values: maps are merged, everything else is replaced."""
    result = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def pinned_to_second_worker() -> dict:
    """Values that put the gateway on one known node, so the tests know which node has a local endpoint."""
    return {"nodeSelector": {"kubernetes.io/hostname": cluster.NODE_WORKER_2}, "topologySpreadConstraints": []}


class Release:
    def __init__(self, name: str, namespace: str, values: dict):
        self.name = name
        self.namespace = namespace
        self.values = values

    @property
    def fullname(self) -> str:
        return self.name if "frank-gateway" in self.name else f"{self.name}-frank-gateway"

    def kubectl(self, *args, **kw):
        return kubectl("--namespace", self.namespace, *args, **kw)

    def install(self, values: dict, wait: bool = True) -> None:
        """helm upgrade --install, also used to upgrade with other values."""
        self.values = values
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as handle:
            yaml.safe_dump(values, handle, width=1000)
        try:
            helm(
                "upgrade", "--install", self.name, str(config.CHART_DIR),
                "--namespace", self.namespace, "--values", handle.name,
                *(["--wait", "--timeout", "5m"] if wait else []),
                timeout=420,
            )
        finally:
            Path(handle.name).unlink(missing_ok=True)

    def upgrade(self, override: dict, wait: bool = True) -> None:
        self.install(merge(self.values, override), wait=wait)

    def wait_ready(self, timeout: int = 180) -> None:
        self.kubectl("rollout", "status", f"deployment/{self.fullname}", f"--timeout={timeout}s")

    def pods(self) -> List[dict]:
        selector = f"app.kubernetes.io/instance={self.name},app.kubernetes.io/component=gateway"
        out = self.kubectl("get", "pods", "-l", selector, "-o", "json").stdout
        return json.loads(out)["items"]

    def service_address(self, service: Optional[str] = None, timeout: int = 90) -> str:
        """The external address that the load balancer gave to a Service."""
        name = service or self.fullname

        def address():
            out = self.kubectl(
                "get", "service", name, "-o", "jsonpath={.status.loadBalancer.ingress[0].ip}"
            ).stdout.strip()
            return out or None

        return wait_until(address, timeout, message=f"an external address for service {name}")

    def service_ip(self, service: Optional[str] = None) -> str:
        out = self.kubectl(
            "get", "service", service or self.fullname, "-o", "jsonpath={.spec.clusterIP}"
        ).stdout.strip()
        return out

    def exec(self, *command, container: str = "gateway", check: bool = True):
        pod = self.pods()[0]["metadata"]["name"]
        return self.kubectl("exec", pod, "-c", container, "--", *command, check=check)

    def get_local(self, path: str, port: int = 9080) -> str:
        """A request from inside the gateway pod to the gateway itself. The image has wget and no curl."""
        result = self.exec("wget", "-q", "-O", "-", "-T", "5", f"http://127.0.0.1:{port}{path}", check=False)
        return result.stdout

    def rollback(self, revision: int) -> None:
        helm("rollback", self.name, str(revision), "--namespace", self.namespace, "--wait", "--timeout", "5m", timeout=420)

    def uninstall(self) -> None:
        helm("uninstall", self.name, "--namespace", self.namespace, "--wait", check=False, timeout=300)
        kubectl("delete", "namespace", self.namespace, "--wait=false", "--ignore-not-found", check=False)

    def diagnostics(self) -> str:
        """Everything that helps to understand a failure."""
        sections = []
        commands = [
            ("resources", ["get", "all,ingress,networkpolicy,httproutes,tlsroutes,gateways", "-o", "wide"]),
            ("events", ["get", "events", "--sort-by=.lastTimestamp"]),
            ("describe pods", ["describe", "pods"]),
            ("logs", ["logs", "-l", f"app.kubernetes.io/instance={self.name}", "--all-containers", "--tail=200", "--prefix"]),
        ]
        for title, args in commands:
            result = self.kubectl(*args, check=False)
            sections.append(f"===== {title}\n{result.stdout}{result.stderr}")
        return "\n".join(sections)


class ClientPod:
    """A pod in a namespace of its own, to test what can reach the gateway from inside the cluster.

    It runs the gateway image, which has wget, and is already on the nodes."""

    def __init__(self, namespace: str, image: str):
        self.namespace = namespace
        self.image = image

    def start(self) -> "ClientPod":
        create_namespace(self.namespace)
        kubectl(
            "--namespace", self.namespace, "run", "client", "--image", self.image, "--restart", "Never",
            "--command", "--", "sleep", "3600",
        )
        kubectl("--namespace", self.namespace, "wait", "--for=condition=Ready", "pod/client", "--timeout=300s")
        return self

    def get(self, url: str, timeout: int = 5):
        """wget the url, once. Returns the completed process, `stdout` is the body.

        wget retries 20 times by default, and a connection that is blocked then takes 20 timeouts to fail.
        A test that expects the request to work after a while polls with wait_until instead.
        """
        return kubectl(
            "--namespace", self.namespace, "exec", "client", "--",
            "wget", "-q", "-O", "-", "--tries=1", "-T", str(timeout), url,
            check=False,
        )


class Deployer:
    """Creates releases, each in a namespace of its own, and removes them again at the end."""

    def __init__(self, pki: Pki, info: ClusterInfo):
        self.pki = pki
        self.info = info
        self.releases: List[Release] = []
        self.namespaces: List[str] = []
        self.hostnames = ("api.e2e.test", "pp.e2e.test", "term.e2e.test", "gw.e2e.test", "other.e2e.test")
        self.server_cert = pki.server("server", *self.hostnames)
        delete_leftover_namespaces()

    def client_pod(self, namespace: str) -> ClientPod:
        pod = ClientPod(namespace, cluster.chart_image()).start()
        self.namespaces.append(namespace)
        return pod

    def base_values(self, **options) -> dict:
        """Values that suit a small test cluster, with the certificates of the gateway in the environment."""
        return {
            "resources": {
                "requests": {"cpu": "50m", "memory": "128Mi"},
                "limits": {"cpu": "1000m", "memory": "1Gi"},
            },
            "env": apisix.TLS_ENV,
            "standalone": {"apisixYaml": apisix.apisix_yaml(**options)},
        }

    def deploy(self, values: Optional[dict] = None, *, name: Optional[str] = None, wait: bool = True) -> Release:
        suffix = uuid.uuid4().hex[:5]
        name = f"{name}-{suffix}" if name else f"gw-{suffix}"
        namespace = f"e2e-{name}"
        log(f"installing release {name} in namespace {namespace}")
        create_namespace(namespace)
        self._create_certs_secret(namespace)
        release = Release(name, namespace, values or self.base_values())
        self.releases.append(release)
        release.install(release.values, wait=wait)
        return release

    def _create_certs_secret(self, namespace: str) -> None:
        secrets = [
            {
                "apiVersion": "v1", "kind": "Secret",
                "metadata": {"name": "gateway-certs", "namespace": namespace},
                "stringData": {
                    "tls.crt": self.server_cert.cert_pem,
                    "tls.key": self.server_cert.key_pem,
                    "ca.crt": self.pki.ca.pem,
                },
            },
            # For an Ingress controller or a Gateway that terminates TLS
            {
                "apiVersion": "v1", "kind": "Secret", "type": "kubernetes.io/tls",
                "metadata": {"name": "listener-tls", "namespace": namespace},
                "stringData": {"tls.crt": self.server_cert.cert_pem, "tls.key": self.server_cert.key_pem},
            },
        ]
        apply(yaml.safe_dump_all(secrets))

    def remove(self, release: Release) -> None:
        if release in self.releases:
            self.releases.remove(release)
        release.uninstall()

    def cleanup(self) -> None:
        if config.KEEP_RELEASES:
            log("E2E_KEEP is set, the releases are kept")
            return
        for release in list(self.releases):
            self.remove(release)
        for namespace in self.namespaces:
            kubectl("delete", "namespace", namespace, "--wait=false", "--ignore-not-found", check=False)
