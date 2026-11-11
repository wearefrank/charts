"""Creates the kind cluster and installs a load balancer, an Ingress controller and a Gateway API implementation."""
import ipaddress
import json
import re
import socket
from dataclasses import dataclass
from pathlib import Path

import yaml

from . import config, router
from .tools import apply, docker, helm, kind, kubectl, log, run, wait_until

KIND_CONFIG = Path(__file__).resolve().parent.parent / "cluster" / "kind.yaml"

NODE_WORKER_1 = f"{config.CLUSTER_NAME}-worker"
NODE_WORKER_2 = f"{config.CLUSTER_NAME}-worker2"


@dataclass
class ClusterInfo:
    subnet: ipaddress.IPv4Network
    runner_ip: str
    client_b_ip: str
    local_pool: tuple  # addresses for LoadBalancer Services, announced by every worker
    cluster_pool: tuple  # addresses that are only announced by the first worker, used on request
    router_ip: str  # the BGP router, in the kind network
    bgp_network: ipaddress.IPv4Network  # addresses that are announced over BGP, outside the kind network


def cluster_exists() -> bool:
    return config.CLUSTER_NAME in kind("get", "clusters").stdout.split()


def create_cluster() -> None:
    if cluster_exists():
        log(f"kind cluster {config.CLUSTER_NAME} exists")
        return
    log(f"creating kind cluster {config.CLUSTER_NAME} with {config.NODE_IMAGE}")
    kind(
        "create", "cluster", "--name", config.CLUSTER_NAME, "--image", config.NODE_IMAGE,
        "--config", str(KIND_CONFIG), "--wait", "180s", timeout=900,
    )


def kind_subnet() -> ipaddress.IPv4Network:
    networks = json.loads(docker("network", "inspect", config.KIND_NETWORK).stdout)
    for entry in networks[0]["IPAM"]["Config"]:
        network = ipaddress.ip_network(entry["Subnet"])
        if network.version == 4:
            return network
    raise RuntimeError("the kind network has no IPv4 subnet")


def connect_runner_to_kind_network() -> None:
    """The runner joins the kind network, so it can reach the API server, the nodes and LoadBalancer addresses."""
    me = socket.gethostname()
    attached = json.loads(docker("inspect", me).stdout)[0]["NetworkSettings"]["Networks"]
    if config.KIND_NETWORK not in attached:
        log(f"connecting the runner to the {config.KIND_NETWORK} network")
        docker("network", "connect", config.KIND_NETWORK, me)


def write_kubeconfig() -> None:
    config.KUBECONFIG.parent.mkdir(parents=True, exist_ok=True)
    internal = kind("get", "kubeconfig", "--name", config.CLUSTER_NAME, "--internal").stdout
    config.KUBECONFIG.write_text(internal)


def runner_ip(subnet: ipaddress.IPv4Network) -> str:
    out = run("ip", "-o", "-4", "addr", "show").stdout
    for match in re.finditer(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)", out):
        if ipaddress.ip_address(match.group(1)) in subnet:
            return match.group(1)
    raise RuntimeError("the runner has no address in the kind network")


def runner_interface(subnet: ipaddress.IPv4Network) -> str:
    out = run("ip", "-o", "-4", "addr", "show").stdout
    for line in out.splitlines():
        parts = line.split()
        address = parts[3].split("/")[0]
        if ipaddress.ip_address(address) in subnet:
            return parts[1]
    raise RuntimeError("the runner has no interface in the kind network")


def plan_addresses(subnet: ipaddress.IPv4Network) -> ClusterInfo:
    top = int(subnet.broadcast_address)
    at = lambda offset: str(ipaddress.ip_address(top - offset))  # noqa: E731
    return ClusterInfo(
        subnet=subnet,
        runner_ip=runner_ip(subnet),
        client_b_ip=at(90),
        local_pool=(at(80), at(51)),
        cluster_pool=(at(50), at(41)),
        router_ip=at(100),
        bgp_network=ipaddress.ip_network(config.BGP_POOL),
    )


def add_second_client_address(info: ClusterInfo) -> None:
    """A second source address for the runner, to test allow lists with two different clients."""
    interface = runner_interface(info.subnet)
    existing = run("ip", "-o", "-4", "addr", "show", "dev", interface).stdout
    if info.client_b_ip not in existing:
        run("ip", "addr", "add", f"{info.client_b_ip}/{info.subnet.prefixlen}", "dev", interface)
    # Every run is a new container that Docker may give the same address. Without this announcement the nodes
    # keep the hardware address of the previous container for a while, and the replies never arrive.
    for address in (info.runner_ip, info.client_b_ip):
        run("arping", "-U", "-c", "2", "-I", interface, address, check=False, timeout=30)


def wait_for_nodes() -> None:
    kubectl("wait", "--for=condition=Ready", "nodes", "--all", "--timeout=180s")


def install_metallb(info: ClusterInfo, bgp: bool = True) -> None:
    if kubectl("get", "namespace", "metallb-system", check=False).returncode != 0:
        log(f"installing MetalLB {config.METALLB_VERSION}")
        url = (
            "https://raw.githubusercontent.com/metallb/metallb/"
            f"{config.METALLB_VERSION}/config/manifests/metallb-native.yaml"
        )
        kubectl("apply", "--server-side", "-f", url)
    kubectl("-n", "metallb-system", "rollout", "status", "deployment/controller", "--timeout=180s")
    kubectl("-n", "metallb-system", "rollout", "status", "daemonset/speaker", "--timeout=180s")
    pools = yaml.safe_dump_all(
        [
            {
                "apiVersion": "metallb.io/v1beta1", "kind": "IPAddressPool",
                "metadata": {"name": "local", "namespace": "metallb-system"},
                "spec": {"addresses": [f"{info.local_pool[0]}-{info.local_pool[1]}"]},
            },
            {
                "apiVersion": "metallb.io/v1beta1", "kind": "IPAddressPool",
                "metadata": {"name": "cluster", "namespace": "metallb-system"},
                "spec": {"addresses": [f"{info.cluster_pool[0]}-{info.cluster_pool[1]}"], "autoAssign": False},
            },
            {
                "apiVersion": "metallb.io/v1beta1", "kind": "L2Advertisement",
                "metadata": {"name": "local", "namespace": "metallb-system"},
                "spec": {"ipAddressPools": ["local"]},
            },
            {
                "apiVersion": "metallb.io/v1beta1", "kind": "L2Advertisement",
                "metadata": {"name": "cluster", "namespace": "metallb-system"},
                "spec": {
                    "ipAddressPools": ["cluster"],
                    "nodeSelectors": [{"matchLabels": {"kubernetes.io/hostname": NODE_WORKER_1}}],
                },
            },
            # BGP mode: the addresses in this pool are announced to the router, not answered with ARP
            *(
                [
                    {
                        "apiVersion": "metallb.io/v1beta1", "kind": "IPAddressPool",
                        "metadata": {"name": "bgp", "namespace": "metallb-system"},
                        "spec": {"addresses": [str(info.bgp_network)], "autoAssign": False},
                    },
                    {
                        "apiVersion": "metallb.io/v1beta2", "kind": "BGPPeer",
                        "metadata": {"name": "router", "namespace": "metallb-system"},
                        "spec": {
                            "myASN": config.METALLB_ASN, "peerASN": config.ROUTER_ASN, "peerAddress": info.router_ip,
                        },
                    },
                    {
                        "apiVersion": "metallb.io/v1beta1", "kind": "BGPAdvertisement",
                        "metadata": {"name": "bgp", "namespace": "metallb-system"},
                        "spec": {"ipAddressPools": ["bgp"]},
                    },
                ]
                if bgp
                else []
            ),
        ]
    )
    # The admission webhook of MetalLB needs a moment before it accepts resources
    wait_until(lambda: apply(pools) or True, timeout=120, message="MetalLB to accept its address pools")


def install_bgp_router(info: ClusterInfo) -> None:
    router.ensure(info.router_ip, info.subnet)
    router.route_runner_to_pool(info.router_ip)
    wait_until(
        lambda: router.established_peers() >= 2, 180,
        message="the MetalLB speakers to set up BGP sessions with the router",
    )


def release_deployed(name: str, namespace: str) -> bool:
    return helm("status", name, "--namespace", namespace, check=False).returncode == 0


def service_address(namespace: str, selector: str, timeout: int = 120) -> str:
    """The external address of a Service found by label, for example the one of an Ingress controller."""

    def address():
        out = kubectl(
            "--namespace", namespace, "get", "service", "-l", selector,
            "-o", "jsonpath={.items[0].status.loadBalancer.ingress[0].ip}",
        ).stdout.strip()
        return out or None

    return wait_until(address, timeout, message=f"an external address for {selector} in {namespace}")


def ingress_address() -> str:
    return service_address("haproxy-ingress", "app.kubernetes.io/name=kubernetes-ingress")


def node_address(node: str) -> str:
    return kubectl(
        "get", "node", node, "-o", "jsonpath={.status.addresses[?(@.type==\"InternalIP\")].address}"
    ).stdout.strip()


def pod_cidr() -> str:
    """The pod network of the cluster, the addresses that the gateway sees from the controllers in front of it."""
    out = kubectl("get", "nodes", "-o", "jsonpath={.items[0].spec.podCIDR}").stdout.strip()
    return str(ipaddress.ip_network(out).supernet(new_prefix=16)) if out else "10.244.0.0/16"


def install_haproxy_ingress() -> None:
    if release_deployed("haproxy-ingress", "haproxy-ingress"):
        return
    log(f"installing HAProxy Ingress controller chart {config.HAPROXY_INGRESS_CHART_VERSION}")
    helm(
        "upgrade", "--install", "haproxy-ingress", "kubernetes-ingress",
        "--repo", "https://haproxytech.github.io/helm-charts",
        "--version", config.HAPROXY_INGRESS_CHART_VERSION,
        "--namespace", "haproxy-ingress", "--create-namespace",
        "--set", "controller.service.type=LoadBalancer",
        "--set", "controller.service.externalTrafficPolicy=Local",
        "--set", "controller.ingressClass=haproxy",
        "--set", "controller.replicaCount=1",
        "--wait", "--timeout", "5m", timeout=400,
    )


def install_envoy_gateway() -> None:
    if release_deployed("eg", "envoy-gateway-system"):
        return
    log(f"installing Envoy Gateway {config.ENVOY_GATEWAY_VERSION}")
    helm(
        "upgrade", "--install", "eg", "oci://docker.io/envoyproxy/gateway-helm",
        "--version", config.ENVOY_GATEWAY_VERSION,
        "--namespace", "envoy-gateway-system", "--create-namespace",
        "--wait", "--timeout", "5m", timeout=400,
    )
    kubectl(
        "wait", "--timeout=5m", "-n", "envoy-gateway-system",
        "deployment/envoy-gateway", "--for=condition=Available",
    )
    apply(
        yaml.safe_dump(
            {
                "apiVersion": "gateway.networking.k8s.io/v1", "kind": "GatewayClass",
                "metadata": {"name": "eg"},
                "spec": {"controllerName": "gateway.envoyproxy.io/gatewayclass-controller"},
            }
        )
    )


def install_prometheus_operator_crds() -> None:
    """Only the CRDs, so the API server accepts a ServiceMonitor."""
    if kubectl("get", "crd", "servicemonitors.monitoring.coreos.com", check=False).returncode == 0:
        return
    log("installing the Prometheus Operator CRDs")
    url = (
        "https://github.com/prometheus-operator/prometheus-operator/releases/download/"
        f"{config.PROMETHEUS_OPERATOR_VERSION}/stripped-down-crds.yaml"
    )
    kubectl("apply", "--server-side", "-f", url)


def chart_image() -> str:
    chart = yaml.safe_load((config.CHART_DIR / "Chart.yaml").read_text())
    values = yaml.safe_load((config.CHART_DIR / "values.yaml").read_text())
    image = values["image"]
    return f"{image['registry']}/{image['repository']}:{image['tag'] or chart['appVersion']}"


def ensure_cluster() -> ClusterInfo:
    wanted = config.components()
    create_cluster()
    connect_runner_to_kind_network()
    write_kubeconfig()
    wait_for_nodes()
    info = plan_addresses(kind_subnet())
    add_second_client_address(info)
    log(f"components: {', '.join(sorted(wanted)) or 'none'}")
    if "prometheus-crds" in wanted:
        install_prometheus_operator_crds()
    if "metallb" in wanted:
        install_metallb(info, bgp="bgp" in wanted)
    if "bgp" in wanted:
        install_bgp_router(info)
    if "haproxy" in wanted:
        install_haproxy_ingress()
    if "envoy-gateway" in wanted:
        install_envoy_gateway()
    log(f"cluster ready: runner {info.runner_ip}, second client {info.client_b_ip}, pool {info.local_pool}")
    return info


def delete_cluster() -> None:
    router.remove()
    if cluster_exists():
        log(f"deleting kind cluster {config.CLUSTER_NAME}")
        kind("delete", "cluster", "--name", config.CLUSTER_NAME)
