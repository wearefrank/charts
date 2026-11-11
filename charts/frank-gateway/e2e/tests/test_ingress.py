"""Traffic that comes in through an Ingress, with the HAProxy Ingress controller.

With TLS passthrough the controller does not look inside the connection, so the gateway terminates TLS and validates
client certificates itself. With a terminating Ingress the controller ends TLS and talks plain HTTP to the gateway.

Every scenario has its own host name, because the controller routes on it and the scenarios exist side by side.
"""
import ipaddress

import pytest

from fge2e import cluster, net
from fge2e.chart import merge
from fge2e.tools import wait_until

pytestmark = pytest.mark.ingress

PASSTHROUGH_HOST = "api.e2e.test"
PROXY_PROTOCOL_HOST = "pp.e2e.test"
TERMINATING_HOST = "term.e2e.test"
PASSTHROUGH = {"haproxy.org/ssl-passthrough": "true"}


def ingress_values(deployer, host, *, annotations=None, tls=False, backend_port="https", **apisix_options):
    ingress = {
        "enabled": True,
        "ingressClassName": "haproxy",
        "annotations": annotations or {},
        "defaultBackendPort": backend_port,
        "rules": [{"host": host, "http": {"paths": [{"path": "/", "pathType": "Prefix"}]}}],
    }
    if tls:
        ingress["tls"] = [{"hosts": [host], "secretName": "listener-tls"}]
    return merge(deployer.base_values(hostnames=(host,), **apisix_options), {"ingress": ingress})


def https(address, pki, host, **kwargs):
    kwargs.setdefault("verify_with", pki.ca.file)
    kwargs.setdefault("path", "/any/echo")
    return net.request(address, host=host, **kwargs)


def wait_for_ingress(address, pki, host, **request):
    wait_until(
        lambda: https(address, pki, host, **request).ok, 120, interval=3, message=f"the Ingress to route {host}"
    )


@pytest.fixture(scope="module")
def controller():
    return cluster.ingress_address()


# ---- TLS passthrough


@pytest.fixture(scope="module")
def passthrough(deployer, controller, pki):
    values = ingress_values(deployer, PASSTHROUGH_HOST, annotations=PASSTHROUGH, mtls=True)
    release = deployer.deploy(name="ingpass", values=values)
    wait_for_ingress(controller, pki, PASSTHROUGH_HOST, client_cert=pki.client("probe").pair)
    yield release
    deployer.remove(release)


def test_the_gateway_serves_its_own_certificate_through_the_ingress(passthrough, controller, pki):
    response = https(controller, pki, PASSTHROUGH_HOST, client_cert=pki.client("alice").pair)
    assert response.ok, response
    assert response.peer_cert.issuer == pki.ca.cert.certificate.subject, "the certificate is not the one of the gateway"
    assert response.json()["server_name"] == PASSTHROUGH_HOST


def test_mtls_is_validated_by_the_gateway_through_the_ingress(passthrough, controller, pki):
    valid = https(controller, pki, PASSTHROUGH_HOST, client_cert=pki.client("alice").pair)
    assert valid.ok, valid
    assert valid.json()["client_verify"] == "SUCCESS"
    assert "CN=alice" in valid.json()["client_dn"]

    assert not https(controller, pki, PASSTHROUGH_HOST).ok, "a request without a client certificate was accepted"
    assert not https(controller, pki, PASSTHROUGH_HOST, client_cert=pki.untrusted_client("mallory").pair).ok
    assert not https(controller, pki, PASSTHROUGH_HOST, client_cert=pki.expired_client("old").pair).ok
    assert https(controller, pki, PASSTHROUGH_HOST, path="/open/echo").ok, "a path that is excluded from mtls needs no certificate"


def test_a_host_name_that_is_not_in_the_ingress_does_not_reach_the_gateway(passthrough, controller, pki):
    response = https(controller, pki, "unknown.e2e.test", verify_with=None, client_cert=pki.client("alice").pair)
    assert not response.ok or response.json().get("server_name") != PASSTHROUGH_HOST


def test_without_proxy_protocol_the_gateway_sees_the_controller_and_not_the_client(passthrough, controller, pki, info):
    """With TLS passthrough the controller opens a new connection, so the client address is lost without PROXY protocol."""
    answer = https(controller, pki, PASSTHROUGH_HOST, source_ip=info.runner_ip, client_cert=pki.client("alice").pair)
    seen = answer.json()["remote_addr"]
    assert seen != info.runner_ip, "the client address was kept, then PROXY protocol is not needed"
    assert ipaddress.ip_address(seen) in ipaddress.ip_network(cluster.pod_cidr()), f"expected a pod address, got {seen}"


# ---- TLS passthrough with PROXY protocol: the client address and an allow list


@pytest.fixture(scope="module")
def proxy_protocol(deployer, controller, pki, info):
    """APISIX listens on a port that expects the PROXY protocol, and the controller sends it."""
    values = merge(
        ingress_values(
            deployer,
            PROXY_PROTOCOL_HOST,
            annotations={**PASSTHROUGH, "haproxy.org/send-proxy-protocol": "proxy-v2"},
            backend_port="https-pp",
            mtls=True,
            allow=[info.runner_ip],
        ),
        {
            "service": {
                "ports": [
                    {"name": "http", "port": 80},
                    {"name": "https", "port": 443},
                    {"name": "https-pp", "port": 444, "targetPort": 9444},
                ]
            },
            "config": {
                "apisix": {"proxy_protocol": {"listen_https_port": 9444}},
                "nginx_config": {"http": {"real_ip_header": "proxy_protocol", "real_ip_from": [cluster.pod_cidr()]}},
            },
        },
    )
    release = deployer.deploy(name="ingpp", values=values)
    wait_for_ingress(controller, pki, PROXY_PROTOCOL_HOST, client_cert=pki.client("probe").pair, source_ip=info.runner_ip)
    yield release
    deployer.remove(release)


def test_with_proxy_protocol_the_gateway_sees_the_real_client_address(proxy_protocol, controller, pki, info):
    certificate = pki.client("alice").pair
    first = https(controller, pki, PROXY_PROTOCOL_HOST, source_ip=info.runner_ip, client_cert=certificate)
    second = https(controller, pki, PROXY_PROTOCOL_HOST, source_ip=info.client_b_ip, client_cert=certificate)
    assert first.json()["remote_addr"] == info.runner_ip
    assert second.json()["remote_addr"] == info.client_b_ip


def test_an_allow_list_works_through_the_ingress_with_proxy_protocol(proxy_protocol, controller, pki, info):
    certificate = pki.client("alice").pair
    allowed = https(controller, pki, PROXY_PROTOCOL_HOST, source_ip=info.runner_ip, client_cert=certificate, path="/echo")
    denied = https(controller, pki, PROXY_PROTOCOL_HOST, source_ip=info.client_b_ip, client_cert=certificate, path="/echo")
    assert allowed.status == 200, allowed
    assert denied.status == 403, denied


# ---- an Ingress that terminates TLS


@pytest.fixture(scope="module")
def terminating(deployer, controller, pki, info):
    """The controller ends TLS and sends HTTP, the gateway reads the client address from X-Forwarded-For."""
    values = merge(
        ingress_values(deployer, TERMINATING_HOST, tls=True, backend_port="http", allow=[info.runner_ip]),
        {
            "config": {
                "nginx_config": {
                    "http": {
                        "real_ip_header": "X-Forwarded-For",
                        "real_ip_recursive": "on",
                        "real_ip_from": [cluster.pod_cidr()],
                    }
                }
            }
        },
    )
    release = deployer.deploy(name="ingterm", values=values)
    wait_for_ingress(controller, pki, TERMINATING_HOST, source_ip=info.runner_ip)
    yield release
    deployer.remove(release)


def test_the_ingress_terminates_tls_with_its_own_certificate(terminating, controller, pki):
    response = https(controller, pki, TERMINATING_HOST)
    assert response.ok, response
    assert response.json()["scheme"] == "http", "the controller should talk plain HTTP to the gateway"


def test_the_client_address_arrives_in_x_forwarded_for_and_an_allow_list_works(terminating, controller, pki, info):
    allowed = https(controller, pki, TERMINATING_HOST, source_ip=info.runner_ip, path="/echo")
    denied = https(controller, pki, TERMINATING_HOST, source_ip=info.client_b_ip, path="/echo")
    assert allowed.status == 200, allowed
    assert denied.status == 403, denied
    seen = https(controller, pki, TERMINATING_HOST, source_ip=info.client_b_ip, path="/any/echo").json()
    assert seen["remote_addr"] == info.client_b_ip


def test_only_the_host_of_the_ingress_reaches_the_gateway(terminating, controller, pki):
    response = https(controller, pki, "unknown.e2e.test", verify_with=None)
    assert response.status in (404, 503), f"another host name was answered: {response}"
