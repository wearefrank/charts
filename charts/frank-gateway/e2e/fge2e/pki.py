"""A small PKI for the tests: a CA, server certificates and the client certificates used for mTLS."""
import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


@dataclass
class Cert:
    certificate: x509.Certificate
    key: rsa.RSAPrivateKey
    cert_file: Path
    key_file: Path

    @property
    def cert_pem(self) -> str:
        return self.certificate.public_bytes(serialization.Encoding.PEM).decode()

    @property
    def key_pem(self) -> str:
        return self.key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        ).decode()

    @property
    def pair(self):
        """The files in the form `ssl.SSLContext.load_cert_chain` takes."""
        return str(self.cert_file), str(self.key_file)


def _key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _name(common_name: str) -> x509.Name:
    return x509.Name(
        [
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Frank Gateway e2e"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )


def _write(directory: Path, stem: str, certificate: x509.Certificate, key) -> Cert:
    directory.mkdir(parents=True, exist_ok=True)
    cert_file = directory / f"{stem}.crt"
    key_file = directory / f"{stem}.key"
    cert_file.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    key_file.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )
    return Cert(certificate, key, cert_file, key_file)


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class Ca:
    def __init__(self, directory: Path, common_name: str):
        self.directory = directory
        self.common_name = common_name
        key = _key()
        subject = _name(common_name)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(_now() - datetime.timedelta(minutes=5))
            .not_valid_after(_now() + datetime.timedelta(days=2))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True, key_cert_sign=True, crl_sign=True, content_commitment=False,
                    key_encipherment=False, data_encipherment=False, key_agreement=False,
                    encipher_only=False, decipher_only=False,
                ),
                critical=True,
            )
            .sign(key, hashes.SHA256())
        )
        self.cert = _write(directory, "ca", certificate, key)

    @property
    def pem(self) -> str:
        return self.cert.cert_pem

    @property
    def file(self) -> str:
        return str(self.cert.cert_file)

    def issue(
        self,
        common_name: str,
        stem: str,
        *,
        dns: Iterable[str] = (),
        server: bool = False,
        client: bool = False,
        not_before: Optional[datetime.datetime] = None,
        not_after: Optional[datetime.datetime] = None,
    ) -> Cert:
        key = _key()
        builder = (
            x509.CertificateBuilder()
            .subject_name(_name(common_name))
            .issuer_name(self.cert.certificate.subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(not_before or (_now() - datetime.timedelta(minutes=5)))
            .not_valid_after(not_after or (_now() + datetime.timedelta(days=1)))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        )
        usages = []
        if server:
            usages.append(ExtendedKeyUsageOID.SERVER_AUTH)
        if client:
            usages.append(ExtendedKeyUsageOID.CLIENT_AUTH)
        if usages:
            builder = builder.add_extension(x509.ExtendedKeyUsage(usages), critical=False)
        names = [x509.DNSName(name) for name in dns]
        if names:
            builder = builder.add_extension(x509.SubjectAlternativeName(names), critical=False)
        certificate = builder.sign(self.cert.key, hashes.SHA256())
        return _write(self.directory, stem, certificate, key)


class Pki:
    """The certificates of a test run."""

    def __init__(self, directory: Path):
        self.ca = Ca(directory / "ca", "Frank Gateway e2e CA")
        self.other_ca = Ca(directory / "other-ca", "Some other CA")
        self.directory = directory

    def server(self, stem: str, *names: str) -> Cert:
        return self.ca.issue(names[0], stem, dns=names, server=True)

    def client(self, common_name: str) -> Cert:
        """A client certificate signed by the trusted CA."""
        return self.ca.issue(common_name, f"client-{common_name}", client=True)

    def untrusted_client(self, common_name: str) -> Cert:
        """A client certificate signed by a CA that the gateway does not trust."""
        return self.other_ca.issue(common_name, f"untrusted-{common_name}", client=True)

    def expired_client(self, common_name: str) -> Cert:
        """A client certificate of the trusted CA that has expired."""
        return self.ca.issue(
            common_name, f"expired-{common_name}", client=True,
            not_before=_now() - datetime.timedelta(days=3), not_after=_now() - datetime.timedelta(days=1),
        )
