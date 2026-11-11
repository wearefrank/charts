"""A BGP router in the kind network. MetalLB announces LoadBalancer addresses to it, like it would to a real router.

The runner sends traffic for those addresses to the router, and the router forwards it to the nodes that announced
them. That is how a LoadBalancer Service works with MetalLB in BGP mode, so it tests the same path.
"""
import hashlib
import ipaddress
import json
import tempfile
from pathlib import Path

from . import config
from .tools import docker, log, run, wait_until

NAME = f"{config.CLUSTER_NAME}-bgp-router"
SETUP_LABEL = "fge2e.setup"

DAEMONS = """\
bgpd=yes
vtysh_enable=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
mgmtd_options="  -A 127.0.0.1"
bgpd_options="   -A 127.0.0.1"
staticd_options="-A 127.0.0.1"
"""

# Every node of the cluster may connect, and the router accepts what it hears without a policy
FRR_CONF = """\
frr defaults traditional
hostname {name}
log stdout informational
!
router bgp {asn}
 bgp router-id {router_ip}
 no bgp ebgp-requires-policy
 neighbor nodes peer-group
 neighbor nodes remote-as {peer_asn}
 bgp listen range {subnet} peer-group nodes
 !
 address-family ipv4 unicast
  maximum-paths 8
 exit-address-family
!
"""


def _inspect():
    result = docker("inspect", NAME, check=False)
    return json.loads(result.stdout)[0] if result.returncode == 0 else None


def ensure(router_ip: str, subnet: ipaddress.IPv4Network) -> None:
    """Starts the router with a fixed address in the kind network, unless it already runs with this setup."""
    files = {
        "daemons": DAEMONS,
        "frr.conf": FRR_CONF.format(
            name=NAME, asn=config.ROUTER_ASN, peer_asn=config.METALLB_ASN, router_ip=router_ip, subnet=subnet,
        ),
        "vtysh.conf": "service integrated-vtysh-config\n",
    }
    # A router from an earlier run is only reused when it has the same image, address and configuration
    setup = hashlib.sha256(json.dumps([config.FRR_IMAGE, router_ip, files], sort_keys=True).encode()).hexdigest()
    current = _inspect()
    if current and current["State"]["Running"] and current["Config"]["Labels"].get(SETUP_LABEL) == setup:
        return
    if current:
        docker("rm", "--force", NAME)
    log(f"starting the BGP router {NAME} at {router_ip}")
    docker(
        "create", "--name", NAME, "--network", config.KIND_NETWORK, "--ip", router_ip, "--label", f"{SETUP_LABEL}={setup}",
        "--cap-add", "NET_ADMIN", "--cap-add", "NET_RAW", "--cap-add", "SYS_ADMIN",
        # It forwards the traffic. Without redirects the traffic keeps flowing through it, and not around it.
        "--sysctl", "net.ipv4.ip_forward=1", "--sysctl", "net.ipv4.conf.all.send_redirects=0",
        config.FRR_IMAGE,
        timeout=900,
    )
    with tempfile.TemporaryDirectory() as directory:
        for name, content in files.items():
            path = Path(directory) / name
            path.write_text(content, newline="\n")
            docker("cp", str(path), f"{NAME}:/etc/frr/{name}")
    docker("start", NAME)
    wait_until(configured, 60, message="the BGP router to start with its configuration")


def remove() -> None:
    if _inspect():
        docker("rm", "--force", NAME)


def route_runner_to_pool(router_ip: str) -> None:
    """The runner reaches the announced addresses through the router, as the clients of a real cluster would."""
    run("ip", "route", "replace", config.BGP_POOL, "via", router_ip)


def vtysh(*commands: str):
    args = []
    for command in commands:
        args += ["-c", command]
    return docker("exec", NAME, "vtysh", *args, check=False)


def configured() -> bool:
    """FRR starts without the configuration that it could not apply, so check that it is there."""
    result = vtysh("show running-config")
    return result.returncode == 0 and "bgp listen range" in result.stdout


def diagnostics() -> str:
    """What the router knows, to understand a failed test."""
    sections = []
    for command in ("show bgp summary", "show ip route bgp", "show bgp ipv4 unicast"):
        result = vtysh(command)
        sections.append(f"## {command}\n{result.stdout}{result.stderr}")
    return "\n".join(sections)


def established_peers() -> int:
    result = vtysh("show bgp summary json")
    if result.returncode != 0:
        return 0
    peers = json.loads(result.stdout).get("ipv4Unicast", {}).get("peers", {})
    return sum(1 for peer in peers.values() if peer.get("state") == "Established")


def next_hops(address: str) -> set:
    """The nodes that the router sends traffic for an address to, which are the nodes that announce it."""
    result = vtysh(f"show ip route {address}/32 json")
    if result.returncode != 0 or not result.stdout.strip():
        return set()
    hops = set()
    for routes in json.loads(result.stdout).values():
        for route in routes:
            if route.get("protocol") != "bgp":
                continue
            hops |= {hop["ip"] for hop in route.get("nexthops", []) if hop.get("ip") and hop.get("active", True)}
    return hops


def announced_by(address: str, nodes: set, timeout: int = 90, exact: bool = True) -> None:
    """Waits until the router sends traffic for an address to these nodes, and with `exact` to no others."""

    def check():
        hops = next_hops(address)
        mismatch = hops != nodes if exact else not nodes <= hops
        if mismatch:
            raise AssertionError(f"the router sends {address} to {sorted(hops)}, expected {sorted(nodes)}")
        return True

    wait_until(check, timeout, message=f"the router to route {address} to {sorted(nodes)}")
