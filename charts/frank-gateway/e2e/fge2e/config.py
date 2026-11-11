"""Settings of the end-to-end tests. Versions of the cluster components are pinned here."""
import os
from pathlib import Path

CLUSTER_NAME = os.environ.get("E2E_CLUSTER_NAME") or "fg-e2e"
KIND_NETWORK = "kind"

# Kubernetes version of the cluster. The default is the node image of the kind release in the Dockerfile.
DEFAULT_NODE_IMAGE = (
    "kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5"
)
NODE_IMAGE = os.environ.get("E2E_KUBE_NODE_IMAGE") or DEFAULT_NODE_IMAGE

# Components that give the cluster its load balancer, Ingress and Gateway API implementation
METALLB_VERSION = "v0.16.2"
HAPROXY_INGRESS_CHART_VERSION = "1.54.4"
ENVOY_GATEWAY_VERSION = "v1.10.0"
PROMETHEUS_OPERATOR_VERSION = "v0.95.1"

# What is installed in the cluster. The default is everything, so a local run can run every test. A CI job installs
# only what its tests need, with E2E_COMPONENTS (a comma separated list), so each cluster configuration is a job.
#   metallb           LoadBalancer addresses, in layer 2 mode
#   bgp               MetalLB in BGP mode, with a router (needs metallb)
#   haproxy           the HAProxy Ingress controller (needs metallb for its address)
#   envoy-gateway     Envoy Gateway and the Gateway API CRDs (needs metallb for the address of a Gateway)
#   prometheus-crds   the CRDs of the Prometheus Operator, so a ServiceMonitor is accepted
# `none` installs nothing, for tests that only need the cluster itself.
COMPONENT_REQUIRES = {"bgp": {"metallb"}, "haproxy": {"metallb"}, "envoy-gateway": {"metallb"}}
ALL_COMPONENTS = {"metallb", "bgp", "haproxy", "envoy-gateway", "prometheus-crds"}


def components() -> set:
    """The components to install: the ones in E2E_COMPONENTS and what they need, all when it is empty, none for `none`."""
    selected = {name.strip() for name in os.environ.get("E2E_COMPONENTS", "").split(",") if name.strip()}
    if selected == {"none"}:
        return set()
    unknown = selected - ALL_COMPONENTS
    if unknown:
        raise ValueError(f"unknown E2E_COMPONENTS {sorted(unknown)}, choose from {sorted(ALL_COMPONENTS)} or none")
    for name in list(selected):
        selected |= COMPONENT_REQUIRES.get(name, set())
    return selected or set(ALL_COMPONENTS)

# The router that MetalLB announces LoadBalancer addresses to in BGP mode. FRR is what MetalLB itself tests against.
FRR_IMAGE = "quay.io/frrouting/frr:10.5.3@sha256:37b42d2b340c322edc5f20dc4598373adb6e813e95cc9d4a18f64f9a37c98a4c"
METALLB_ASN = 64500
ROUTER_ASN = 64501
# Documentation range (TEST-NET-2): it is never routed on a real network, so it cannot clash with the kind network
BGP_POOL = "198.51.100.0/24"

CHART_DIR = Path(os.environ.get("CHART_DIR", "/repo/charts/frank-gateway"))
RESULTS_DIR = Path(os.environ.get("E2E_RESULTS_DIR", "/results"))
KEEP_RELEASES = os.environ.get("E2E_KEEP", "") not in ("", "0", "false")

KUBECONFIG = Path.home() / ".kube" / "config"
