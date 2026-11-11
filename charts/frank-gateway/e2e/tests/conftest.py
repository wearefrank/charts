"""Fixtures of the end-to-end tests. The cluster is created by `python -m fge2e up` before pytest starts."""
import re

import pytest

from fge2e import cluster, config, router
from fge2e.chart import Deployer
from fge2e.pki import Pki

_deployer = None


@pytest.fixture(scope="session")
def info():
    return cluster.plan_addresses(cluster.kind_subnet())


@pytest.fixture(scope="session")
def pki(tmp_path_factory):
    return Pki(tmp_path_factory.mktemp("pki"))


@pytest.fixture(scope="session")
def deployer(pki, info):
    global _deployer
    _deployer = Deployer(pki, info)
    yield _deployer
    _deployer.cleanup()


@pytest.fixture(scope="session")
def client_a(info):
    """The address of the runner, the first client."""
    return info.runner_ip


@pytest.fixture(scope="session")
def client_b(info):
    """A second source address of the runner, the second client."""
    return info.client_b_ip


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Keeps what is needed to understand a failure: the state of every release, and the logs of the gateway."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed or _deployer is None:
        return
    directory = config.RESULTS_DIR / "failures" / re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)
    directory.mkdir(parents=True, exist_ok=True)
    for release in _deployer.releases:
        (directory / f"{release.name}.txt").write_text(release.diagnostics())
    if item.get_closest_marker("bgp"):
        (directory / "bgp-router.txt").write_text(router.diagnostics())
