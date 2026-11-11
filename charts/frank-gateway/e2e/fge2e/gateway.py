"""A Gateway of Envoy Gateway for the tests. The chart only creates the routes, the Gateway belongs to the user."""
import yaml

from .tools import apply, kubectl, wait_until

GATEWAY_NAME = "e2e-gateway"
TERMINATE_HOST = "gw.e2e.test"


def create_gateway(namespace: str, *, keep_client_address: bool = True) -> str:
    """Creates a Gateway with an HTTPS listener that terminates TLS and a TLS listener that passes it through.

    Envoy Gateway starts a proxy with a LoadBalancer Service for it. With keep_client_address the Service gets
    externalTrafficPolicy Local, which is what keeps the client address for allow lists. Returns the address.
    """
    documents = [
        {
            "apiVersion": "gateway.envoyproxy.io/v1alpha1", "kind": "EnvoyProxy",
            "metadata": {"name": "e2e-proxy", "namespace": namespace},
            "spec": {
                "provider": {
                    "type": "Kubernetes",
                    "kubernetes": {
                        "envoyService": {
                            "type": "LoadBalancer",
                            "externalTrafficPolicy": "Local" if keep_client_address else "Cluster",
                        }
                    },
                }
            },
        },
        {
            "apiVersion": "gateway.networking.k8s.io/v1", "kind": "Gateway",
            "metadata": {"name": GATEWAY_NAME, "namespace": namespace},
            "spec": {
                "gatewayClassName": "eg",
                "infrastructure": {
                    "parametersRef": {"group": "gateway.envoyproxy.io", "kind": "EnvoyProxy", "name": "e2e-proxy"}
                },
                "listeners": [
                    {
                        "name": "https",
                        "port": 443,
                        "protocol": "HTTPS",
                        "hostname": TERMINATE_HOST,
                        "tls": {"mode": "Terminate", "certificateRefs": [{"kind": "Secret", "name": "listener-tls"}]},
                        "allowedRoutes": {"namespaces": {"from": "Same"}, "kinds": [{"kind": "HTTPRoute"}]},
                    },
                    {
                        "name": "tls-passthrough",
                        "port": 8443,
                        "protocol": "TLS",
                        "tls": {"mode": "Passthrough"},
                        "allowedRoutes": {"namespaces": {"from": "Same"}, "kinds": [{"kind": "TLSRoute"}]},
                    },
                ],
            },
        },
    ]
    apply(yaml.safe_dump_all(documents))

    def address():
        out = kubectl(
            "--namespace", namespace, "get", "gateway", GATEWAY_NAME,
            "-o", "jsonpath={.status.addresses[0].value}",
        ).stdout.strip()
        return out or None

    return wait_until(address, 180, interval=3, message="the Gateway to get an address")


def route_conditions(namespace: str, kind: str, name: str) -> dict:
    """The conditions of a route for its first parent, for example {'Accepted': 'True', 'ResolvedRefs': 'True'}."""
    out = kubectl(
        "--namespace", namespace, "get", kind, name,
        "-o", "jsonpath={range .status.parents[0].conditions[*]}{.type}={.status}{\" \"}{end}",
        check=False,
    ).stdout
    return dict(item.split("=") for item in out.split())
