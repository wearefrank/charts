"""The APISIX routes the tests use, as the contents of apisix.yaml."""
import textwrap
from typing import Iterable, Optional, Sequence

import yaml

# Answers with what APISIX knows about the connection, so tests can see the client address,
# the TLS parameters and the client certificate as the gateway saw them.
ECHO = textwrap.dedent(
    """\
    return function(conf, ctx)
      return 200, {
        remote_addr = ngx.var.remote_addr,
        x_forwarded_for = ngx.var.http_x_forwarded_for,
        host = ngx.var.host,
        scheme = ngx.var.scheme,
        server_name = ngx.var.ssl_server_name,
        tls_protocol = ngx.var.ssl_protocol,
        tls_cipher = ngx.var.ssl_cipher,
        http_version = ngx.var.server_protocol,
        client_verify = ngx.var.ssl_client_verify,
        client_dn = ngx.var.ssl_client_s_dn,
        pod = ngx.var.hostname,
      }
    end
    """
)

TLS_ENV = [
    {"name": "TLS_CERT", "valueFrom": {"secretKeyRef": {"name": "gateway-certs", "key": "tls.crt"}}},
    {"name": "TLS_KEY", "valueFrom": {"secretKeyRef": {"name": "gateway-certs", "key": "tls.key"}}},
    {"name": "CLIENT_CA", "valueFrom": {"secretKeyRef": {"name": "gateway-certs", "key": "ca.crt"}}},
]


def _echo_plugins(allow: Optional[Sequence[str]]):
    # serverless-post-function runs after the other plugins of the access phase, such as ip-restriction
    plugins = {"serverless-post-function": {"phase": "access", "functions": [ECHO]}}
    if allow is not None:
        plugins["ip-restriction"] = {"whitelist": list(allow), "message": "denied by the e2e allow list"}
    return plugins


def apisix_yaml(
    *,
    hostnames: Iterable[str] = ("api.e2e.test",),
    mtls: bool = False,
    skip_mtls_uri_regex: Sequence[str] = ("^/open",),
    allow: Optional[Sequence[str]] = None,
    backend: Optional[str] = None,
    tls: bool = True,
    prometheus: bool = False,
) -> str:
    """Routes:

    /echo      what the gateway knows about the request, behind an optional allow list of client addresses
    /open/echo the same without an allow list, and exempt from the client certificate when mtls is on
    /any/echo  the same, without an allow list, but with the client certificate when mtls is on
    /slow      answers after 5 seconds
    /slow-long answers after 20 seconds, longer than the preStop sleep of the chart
    /backend/* proxies to an upstream, when `backend` (host:port) is given
    """
    document = {}
    if tls:
        ssl = {"cert": "${{TLS_CERT}}", "key": "${{TLS_KEY}}", "snis": list(hostnames)}
        if mtls:
            ssl["client"] = {
                "ca": "${{CLIENT_CA}}",
                "depth": 2,
                "skip_mtls_uri_regex": list(skip_mtls_uri_regex),
            }
        document["ssls"] = [ssl]
    routes = [
        {"id": "echo", "uri": "/echo", "plugins": _echo_plugins(allow)},
        {"id": "open-echo", "uri": "/open/echo", "plugins": _echo_plugins(None)},
        {"id": "any-echo", "uri": "/any/echo", "plugins": _echo_plugins(None)},
        {
            "id": "slow",
            "uri": "/slow",
            "plugins": {"mocking": {"delay": 5, "response_example": "slow", "content_type": "text/plain"}},
        },
        {
            "id": "slow-long",
            "uri": "/slow-long",
            "plugins": {"mocking": {"delay": 20, "response_example": "slow-long", "content_type": "text/plain"}},
        },
    ]
    if backend:
        routes.append(
            {
                "id": "backend",
                "uri": "/backend/*",
                "plugins": {"proxy-rewrite": {"regex_uri": ["^/backend/(.*)", "/$1"]}},
                "upstream": {"type": "roundrobin", "nodes": {backend: 1}},
            }
        )
    document["routes"] = routes
    if prometheus:
        document["global_rules"] = [{"id": "prometheus", "plugins": {"prometheus": {}}}]
    return yaml.safe_dump(document, sort_keys=False, width=1000)
