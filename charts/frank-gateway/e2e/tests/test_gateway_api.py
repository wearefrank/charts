"""Traffic that comes in through Gateway API routes, with Envoy Gateway.

An HTTPRoute is for a Gateway that terminates TLS. A TLSRoute is for TLS passthrough, so the gateway terminates TLS and
validates client certificates itself.
"""
import ipaddress
import re

import pytest

from fge2e import cluster, net
from fge2e.chart import merge
from fge2e.gateway import GATEWAY_NAME, TERMINATE_HOST, create_gateway, route_conditions
from fge2e.tools import helm, wait_until

pytestmark = pytest.mark.gateway_api

PASSTHROUGH_HOSTS = ("api.e2e.test", "other.e2e.test")
PASSTHROUGH_PORT = 8443


@pytest.fixture(scope="module")
def routes(deployer, pki, info):
    """One release with an HTTPRoute and a TLSRoute, behind a Gateway that keeps the client address."""
    values = merge(
        deployer.base_values(hostnames=PASSTHROUGH_HOSTS, mtls=True, allow=[info.runner_ip]),
        {
            "httpRoute": {
                "enabled": True,
                "hostnames": [TERMINATE_HOST],
                "parentRefs": [{"name": GATEWAY_NAME, "sectionName": "https"}],
            },
            "tlsRoute": {
                "enabled": True,
                "hostnames": list(PASSTHROUGH_HOSTS),
                "parentRefs": [{"name": GATEWAY_NAME, "sectionName": "tls-passthrough"}],
            },
            "config": {
                "nginx_config": {
                    "http": {
                        "real_ip_header": "X-Forwarded-For",
                        "real_ip_recursive": "on",
                        "real_ip_from": [cluster.pod_cidr()],
                    }
                }
            },
        },
    )
    release = deployer.deploy(name="gwapi", values=values)
    address = create_gateway(release.namespace)
    wait_until(
        lambda: net.request(address, host=TERMINATE_HOST, verify_with=pki.ca.file, path="/any/echo").ok,
        180, interval=3, message="the HTTPRoute to carry traffic",
    )
    yield release, address
    deployer.remove(release)


# ---- the routes in the cluster


def test_the_routes_are_accepted_and_their_backend_is_resolved(routes):
    release, _ = routes
    for kind in ("httproute", "tlsroute"):
        conditions = wait_until(
            lambda kind=kind: (
                route_conditions(release.namespace, kind, release.fullname).get("Accepted") == "True"
                and route_conditions(release.namespace, kind, release.fullname)
            ),
            120, interval=3, message=f"the {kind} to be accepted",
        )
        assert conditions["ResolvedRefs"] == "True", f"the backend of the {kind} is not resolved: {conditions}"


def test_the_chart_uses_the_newest_tlsroute_version_that_the_cluster_serves(routes):
    """The cluster serves v1, so the chart must not fall back to v1alpha2."""
    release, _ = routes
    manifest = helm("get", "manifest", release.name, "--namespace", release.namespace).stdout
    match = re.search(r"apiVersion: (\S+)\nkind: TLSRoute", manifest)
    assert match, "the release has no TLSRoute"
    assert match.group(1) == "gateway.networking.k8s.io/v1"


# ---- HTTPRoute: the Gateway terminates TLS


def test_the_gateway_terminates_tls_and_sends_http_to_the_gateway(routes, pki):
    _, address = routes
    response = net.request(address, host=TERMINATE_HOST, verify_with=pki.ca.file, path="/any/echo")
    assert response.ok, response
    assert response.peer_cert.issuer == pki.ca.cert.certificate.subject
    assert response.json()["scheme"] == "http", "the Gateway should talk plain HTTP to the gateway"


def test_a_host_name_that_the_httproute_does_not_have_is_not_routed(routes, pki):
    _, address = routes
    response = net.request(address, host="unknown.e2e.test", verify_with=None, path="/any/echo")
    assert not response.ok, f"another host name was answered: {response}"


def test_the_client_address_reaches_the_gateway_and_an_allow_list_works_behind_an_httproute(routes, pki, info):
    _, address = routes
    options = {"host": TERMINATE_HOST, "verify_with": pki.ca.file}
    seen = net.request(address, source_ip=info.client_b_ip, path="/any/echo", **options).json()
    assert seen["remote_addr"] == info.client_b_ip
    allowed = net.request(address, source_ip=info.runner_ip, path="/echo", **options)
    denied = net.request(address, source_ip=info.client_b_ip, path="/echo", **options)
    assert allowed.status == 200, allowed
    assert denied.status == 403, denied


# ---- TLSRoute: TLS passes through to the gateway


def passthrough(address, pki, host, **kwargs):
    kwargs.setdefault("verify_with", pki.ca.file)
    kwargs.setdefault("path", "/any/echo")
    return net.request(address, port=PASSTHROUGH_PORT, host=host, **kwargs)


def test_the_gateway_serves_its_own_certificate_through_the_tlsroute(routes, pki):
    _, address = routes
    response = wait_until(
        lambda: (r := passthrough(address, pki, PASSTHROUGH_HOSTS[0], client_cert=pki.client("alice").pair)).ok and r,
        120, interval=3, message="the TLSRoute to carry traffic",
    )
    assert response.peer_cert.issuer == pki.ca.cert.certificate.subject
    assert response.json()["server_name"] == PASSTHROUGH_HOSTS[0]


def test_every_host_name_of_the_tlsroute_is_routed_by_its_sni(routes, pki):
    _, address = routes
    for host in PASSTHROUGH_HOSTS:
        response = passthrough(address, pki, host, client_cert=pki.client("alice").pair)
        assert response.ok, f"{host}: {response}"
        assert response.json()["server_name"] == host
    other = passthrough(address, pki, "unknown.e2e.test", verify_with=None, client_cert=pki.client("alice").pair)
    assert not other.ok, f"a host name that is not in the TLSRoute was answered: {other}"


def test_mtls_is_validated_by_the_gateway_through_the_tlsroute(routes, pki):
    _, address = routes
    host = PASSTHROUGH_HOSTS[0]
    valid = passthrough(address, pki, host, client_cert=pki.client("alice").pair)
    assert valid.ok, valid
    assert valid.json()["client_verify"] == "SUCCESS"
    assert "CN=alice" in valid.json()["client_dn"]
    assert not passthrough(address, pki, host).ok, "a request without a client certificate was accepted"
    assert not passthrough(address, pki, host, client_cert=pki.untrusted_client("mallory").pair).ok
    assert not passthrough(address, pki, host, client_cert=pki.expired_client("old").pair).ok
    assert passthrough(address, pki, host, path="/open/echo").ok


def test_through_a_tlsroute_the_gateway_sees_the_proxy_and_not_the_client(routes, pki, info):
    """With TLS passthrough the proxy opens a new connection, so the client address is lost."""
    _, address = routes
    answer = passthrough(address, pki, PASSTHROUGH_HOSTS[0], source_ip=info.runner_ip, client_cert=pki.client("alice").pair)
    seen = answer.json()["remote_addr"]
    assert seen != info.runner_ip, "the client address was kept through the TLS passthrough"
    assert ipaddress.ip_address(seen) in ipaddress.ip_network(cluster.pod_cidr()), f"expected a pod address, got {seen}"
