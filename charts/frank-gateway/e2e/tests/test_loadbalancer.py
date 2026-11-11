"""Traffic that comes in through a Service of type LoadBalancer with MetalLB in layer 2 mode.

What the gateway does with TLS, mTLS and plugins is tested on the image, in the gateway repository. These tests
check the Service and what the chart passes on: the external address, the client address and the certificates.
"""
import ipaddress

import pytest

from fge2e import net
from fge2e.chart import merge, pinned_to_second_worker
from fge2e.tools import wait_until

pytestmark = pytest.mark.lb


@pytest.fixture(scope="module")
def tls_gateway(deployer, info):
    """TLS ends at the gateway, which only lets the first client address in. Local traffic policy keeps the client address."""
    values = merge(
        deployer.base_values(allow=[info.runner_ip]),
        merge(
            pinned_to_second_worker(),
            {"service": {"type": "LoadBalancer", "externalTrafficPolicy": "Local"}},
        ),
    )
    release = deployer.deploy(name="lbtls", values=values)
    address = release.service_address()
    wait_until(lambda: net.request(address, port=80, tls=False, path="/any/echo").ok, 90, message="the external address")
    yield release, address
    deployer.remove(release)


@pytest.fixture(scope="module")
def mtls_gateway(deployer):
    values = merge(
        deployer.base_values(mtls=True),
        merge(pinned_to_second_worker(), {"service": {"type": "LoadBalancer", "externalTrafficPolicy": "Local"}}),
    )
    release = deployer.deploy(name="lbmtls", values=values)
    address = release.service_address()
    wait_until(
        lambda: net.request(address, path="/open/echo", verify_with=str(deployer.pki.ca.file)).ok,
        90, message="the external address",
    )
    yield release, address
    deployer.remove(release)


def https(address, pki, **kwargs):
    kwargs.setdefault("verify_with", pki.ca.file)
    kwargs.setdefault("path", "/any/echo")
    return net.request(address, **kwargs)


# ---- the external address


def test_the_service_gets_an_external_address_from_the_pool(tls_gateway, info):
    _, address = tls_gateway
    assert ipaddress.ip_address(address) in info.subnet
    low, high = (int(ipaddress.ip_address(a)) for a in info.local_pool)
    assert low <= int(ipaddress.ip_address(address)) <= high


def test_http_and_https_answer_on_the_external_address(tls_gateway, pki):
    _, address = tls_gateway
    plain = net.request(address, port=80, tls=False, path="/any/echo")
    assert plain.ok, plain
    assert plain.json()["scheme"] == "http"
    secure = https(address, pki)
    assert secure.ok, secure
    assert secure.json()["scheme"] == "https"


# ---- SSL termination


def test_the_defaults_of_the_chart_for_tls_versions_and_ciphers_reach_the_gateway(tls_gateway, pki):
    """TLS itself is tested on the image, in the gateway repository (tests/image-behaviour).

    This only shows that the defaults of `config.apisix.ssl` of the chart are what the running gateway uses.
    """
    _, address = tls_gateway
    strong = https(address, pki, tls_max="TLSv1.2", ciphers="ECDHE-RSA-AES256-GCM-SHA384")
    assert strong.ok, strong
    assert strong.tls_version == "TLSv1.2"
    assert not https(address, pki, tls_min="TLSv1.1", tls_max="TLSv1.1").ok, "TLS 1.1 was accepted"
    assert not https(address, pki, tls_max="TLSv1.2", ciphers="AES256-SHA:@SECLEVEL=0").ok, "a weak cipher was accepted"


# ---- the client address, for allow lists


def test_the_gateway_sees_the_real_client_address_and_an_allow_list_works(tls_gateway, info, pki):
    """externalTrafficPolicy Local keeps the source address, so ip-restriction can tell the clients apart."""
    _, address = tls_gateway
    first = https(address, pki, source_ip=info.runner_ip, path="/any/echo")
    second = https(address, pki, source_ip=info.client_b_ip, path="/any/echo")
    assert first.ok, f"first client: {first}"
    assert second.ok, f"second client: {second}"
    assert first.json()["remote_addr"] == info.runner_ip
    assert second.json()["remote_addr"] == info.client_b_ip

    allowed = https(address, pki, source_ip=info.runner_ip, path="/echo")
    denied = https(address, pki, source_ip=info.client_b_ip, path="/echo")
    assert allowed.status == 200, allowed
    assert denied.status == 403, denied
    assert "denied by the e2e allow list" in denied.text


def test_with_the_default_traffic_policy_the_client_address_is_lost(deployer, info, pki):
    """Documents why the chart needs Local: with Cluster the gateway sees a node address, and an allow list fails."""
    values = merge(
        deployer.base_values(allow=[info.runner_ip]),
        merge(
            pinned_to_second_worker(),
            {"service": {"type": "LoadBalancer", "annotations": {"metallb.universe.tf/address-pool": "cluster"}}},
        ),
    )
    release = deployer.deploy(name="lbcluster", values=values)
    try:
        address = release.service_address()
        wait_until(lambda: https(address, pki, source_ip=info.runner_ip).ok, 90, message="the external address")
        seen = https(address, pki, source_ip=info.runner_ip, path="/any/echo").json()["remote_addr"]
        assert seen != info.runner_ip, "the client address was kept, the test does not show the problem"
        assert ipaddress.ip_address(seen) in info.subnet, f"expected the address of a node, got {seen}"
        assert https(address, pki, source_ip=info.runner_ip, path="/echo").status == 403
    finally:
        deployer.remove(release)


# ---- mTLS. The gateway validates the certificates, which is tested on the image (tests/image-behaviour in the gateway
# repository). These two tests show that the CA and the certificate reach it through the `env` values of the chart.


def test_a_valid_client_certificate_is_accepted_and_known_to_the_gateway(mtls_gateway, pki):
    _, address = mtls_gateway
    response = https(address, pki, client_cert=pki.client("alice").pair)
    assert response.ok, response
    answer = response.json()
    assert answer["client_verify"] == "SUCCESS"
    assert "CN=alice" in answer["client_dn"]


def test_a_request_without_a_client_certificate_is_refused(mtls_gateway, pki):
    _, address = mtls_gateway
    response = https(address, pki)
    assert not response.ok, f"a request without a client certificate was accepted: {response}"
