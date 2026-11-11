"""A small HTTP and TLS client for the tests.

It connects to an address and sets the SNI name and the Host header itself, so the tests do not depend on DNS.
It can bind a source address, use a client certificate, limit the TLS version and the ciphers, and it reports
what was negotiated. Failures are returned in `Response.error`, so tests can assert on them.
"""
import json
import socket
import ssl
from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence, Tuple

from cryptography import x509

TLS_VERSIONS = {
    "TLSv1": ssl.TLSVersion.TLSv1,
    "TLSv1.1": ssl.TLSVersion.TLSv1_1,
    "TLSv1.2": ssl.TLSVersion.TLSv1_2,
    "TLSv1.3": ssl.TLSVersion.TLSv1_3,
}


@dataclass
class Response:
    status: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    error: Optional[str] = None
    tls_version: Optional[str] = None
    cipher: Optional[str] = None
    alpn: Optional[str] = None
    peer_cert: Optional[x509.Certificate] = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.status is not None and 200 <= self.status < 300

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json(self):
        return json.loads(self.body)

    def __str__(self) -> str:
        if self.error:
            return f"error: {self.error}"
        return f"HTTP {self.status} {self.text[:300]!r}"


def _context(
    verify_with: Optional[str],
    client_cert: Optional[Tuple[str, str]],
    tls_min: Optional[str],
    tls_max: Optional[str],
    ciphers: Optional[str],
    alpn: Sequence[str],
) -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if verify_with:
        context.load_verify_locations(cafile=verify_with)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
    else:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    if tls_min or tls_max:
        # Old protocol versions are only allowed when the security level is lowered
        context.set_ciphers("ALL:@SECLEVEL=0")
    if tls_min:
        context.minimum_version = TLS_VERSIONS[tls_min]
    if tls_max:
        context.maximum_version = TLS_VERSIONS[tls_max]
    if ciphers:
        context.set_ciphers(ciphers)
    if client_cert:
        context.load_cert_chain(*client_cert)
    context.set_alpn_protocols(list(alpn))
    return context


def _read_all(sock) -> bytes:
    chunks = []
    while True:
        try:
            chunk = sock.recv(65536)
        except ssl.SSLZeroReturnError:
            break
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def _parse(raw: bytes):
    head, _, body = raw.partition(b"\r\n\r\n")
    lines = head.decode("latin-1").split("\r\n")
    status = int(lines[0].split(" ")[1])
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    if headers.get("transfer-encoding", "").lower() == "chunked":
        decoded, rest = b"", body
        while rest:
            size_line, _, rest = rest.partition(b"\r\n")
            size = int(size_line.split(b";")[0] or b"0", 16)
            if size == 0:
                break
            decoded, rest = decoded + rest[:size], rest[size + 2:]
        body = decoded
    return status, headers, body


def request(
    address: str,
    *,
    port: int = 443,
    host: str = "api.e2e.test",
    path: Optional[str] = "/",
    tls: bool = True,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[bytes] = None,
    server_name: Optional[str] = None,
    verify_with: Optional[str] = None,
    client_cert: Optional[Tuple[str, str]] = None,
    source_ip: Optional[str] = None,
    tls_min: Optional[str] = None,
    tls_max: Optional[str] = None,
    ciphers: Optional[str] = None,
    alpn: Sequence[str] = ("http/1.1",),
    timeout: float = 10.0,
) -> Response:
    """Sends one request. With path=None only the TLS handshake is done."""
    response = Response()
    sock = None
    try:
        sock = socket.create_connection(
            (address, port), timeout=timeout, source_address=(source_ip, 0) if source_ip else None
        )
        if tls:
            context = _context(verify_with, client_cert, tls_min, tls_max, ciphers, alpn)
            sock = context.wrap_socket(sock, server_hostname=server_name or host)
            response.tls_version = sock.version()
            cipher = sock.cipher()
            response.cipher = cipher[0] if cipher else None
            response.alpn = sock.selected_alpn_protocol()
            der = sock.getpeercert(binary_form=True)
            if der:
                response.peer_cert = x509.load_der_x509_certificate(der)
        if path is None:
            return response
        lines = [f"{method} {path} HTTP/1.1", f"Host: {host}", "Connection: close"]
        for name, value in (headers or {}).items():
            lines.append(f"{name}: {value}")
        if body is not None:
            lines.append(f"Content-Length: {len(body)}")
        sock.sendall(("\r\n".join(lines) + "\r\n\r\n").encode() + (body or b""))
        raw = _read_all(sock)
        if not raw:
            response.error = "the connection was closed without a response"
            return response
        response.status, response.headers, response.body = _parse(raw)
    except (OSError, ssl.SSLError, ValueError) as error:
        response.error = f"{type(error).__name__}: {error}"
    finally:
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass
    return response
