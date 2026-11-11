"""A LoadBalancer Service with MetalLB in BGP mode: the addresses are announced to a router, which routes to the nodes.

In layer 2 mode (test_loadbalancer.py) one node answers for an address and the clients are on the same network. With
BGP the clients reach the address through a router, which has a route to every node that announced it. The router is
an FRR container in the kind network, and the runner sends traffic for the pool through it (see fge2e/router.py).
"""
import ipaddress

import pytest

from fge2e import net, router
from fge2e.chart import merge, pinned_to_second_worker
from fge2e.cluster import NODE_WORKER_1, NODE_WORKER_2, node_address, pod_cidr
from fge2e.tools import run, wait_until

pytestmark = pytest.mark.bgp

BGP_POOL = {"metallb.universe.tf/address-pool": "bgp"}


def https(address, pki, **kwargs):
    kwargs.setdefault("verify_with", pki.ca.file)
    kwargs.setdefault("path", "/any/echo")
    return net.request(address, **kwargs)


@pytest.fixture(scope="module")
def bgp_gateway(deployer, info):
    """The gateway on the second worker with Local traffic policy, and an allow list for the first client."""
    values = merge(
        deployer.base_values(allow=[info.runner_ip]),
        merge(
            pinned_to_second_worker(),
            {"service": {"type": "LoadBalancer", "externalTrafficPolicy": "Local", "annotations": BGP_POOL}},
        ),
    )
    release = deployer.deploy(name="bgp", values=values)
    address = release.service_address()
    router.announced_by(address, {node_address(NODE_WORKER_2)})
    wait_until(lambda: net.request(address, port=80, tls=False, path="/any/echo").ok, 90, message="the BGP address")
    yield release, address
    deployer.remove(release)


def test_the_bgp_sessions_with_the_router_are_established():
    assert router.established_peers() >= 2


def test_the_service_gets_an_address_outside_the_node_network(bgp_gateway, info):
    _, address = bgp_gateway
    assert ipaddress.ip_address(address) in info.bgp_network
    assert ipaddress.ip_address(address) not in info.subnet


def test_with_local_traffic_policy_only_the_node_with_the_gateway_announces_the_address(bgp_gateway):
    """A node without a local endpoint would drop the traffic, so MetalLB must not attract it."""
    _, address = bgp_gateway
    assert router.next_hops(address) == {node_address(NODE_WORKER_2)}


def test_http_and_https_answer_through_the_router(bgp_gateway, info, pki):
    _, address = bgp_gateway
    assert f"via {info.router_ip}" in run("ip", "route", "get", address).stdout, "the traffic does not use the router"
    plain = net.request(address, port=80, tls=False, path="/any/echo")
    assert plain.ok, plain
    secure = https(address, pki)
    assert secure.ok, secure
    assert secure.json()["scheme"] == "https"
    assert secure.peer_cert.issuer == pki.ca.cert.certificate.subject


def test_the_gateway_sees_the_real_client_address_and_an_allow_list_works(bgp_gateway, info, pki):
    """The router forwards the packets without changing the source address, and Local keeps it on the node."""
    _, address = bgp_gateway
    first = https(address, pki, source_ip=info.runner_ip)
    second = https(address, pki, source_ip=info.client_b_ip)
    assert first.ok, f"first client: {first}"
    assert second.ok, f"second client: {second}"
    assert first.json()["remote_addr"] == info.runner_ip
    assert second.json()["remote_addr"] == info.client_b_ip

    allowed = https(address, pki, source_ip=info.runner_ip, path="/echo")
    denied = https(address, pki, source_ip=info.client_b_ip, path="/echo")
    assert allowed.status == 200, allowed
    assert denied.status == 403, denied


def test_the_address_is_withdrawn_when_the_gateway_is_gone(bgp_gateway):
    """Traffic must not be attracted to a node that has nothing to answer it, for example while the pod moves."""
    release, address = bgp_gateway
    release.kubectl("scale", "deployment", release.fullname, "--replicas=0")
    try:
        router.announced_by(address, set(), timeout=120)
    finally:
        release.kubectl("scale", "deployment", release.fullname, "--replicas=1")
        release.wait_ready()
    router.announced_by(address, {node_address(NODE_WORKER_2)}, timeout=120)


def test_with_the_default_traffic_policy_every_node_announces_the_address_and_the_client_address_is_lost(
    deployer, info, pki
):
    values = merge(
        deployer.base_values(allow=[info.runner_ip]),
        merge(pinned_to_second_worker(), {"service": {"type": "LoadBalancer", "annotations": BGP_POOL}}),
    )
    release = deployer.deploy(name="bgpcluster", values=values)
    try:
        address = release.service_address()
        workers = {node_address(NODE_WORKER_1), node_address(NODE_WORKER_2)}
        router.announced_by(address, workers, exact=False)
        wait_until(lambda: https(address, pki, source_ip=info.runner_ip).ok, 90, message="the BGP address")
        seen = https(address, pki, source_ip=info.runner_ip).json()["remote_addr"]
        assert seen != info.runner_ip, "the client address was kept, the test does not show the problem"
        # The router chooses a node for each connection. kube-proxy replaces the client address with the address of the
        # node when the connection has to go to another node, and with the address of the pod network of the node when
        # the pod is on the node that got the connection.
        seen_address = ipaddress.ip_address(seen)
        assert seen_address in info.subnet or seen_address in ipaddress.ip_network(pod_cidr()), (
            f"expected the address of a node or of its pod network, got {seen}"
        )
        assert https(address, pki, source_ip=info.runner_ip, path="/echo").status == 403
    finally:
        deployer.remove(release)
