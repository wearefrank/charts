"""Command line of the runner: up, down, test and shell."""
import os
import subprocess
import sys

from . import cluster, config
from .tools import die, log


def _up() -> None:
    cluster.ensure_cluster()


def _test(extra) -> int:
    _up()
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    args = [
        sys.executable, "-m", "pytest", "-ra", "--color=yes",
        f"--junitxml={config.RESULTS_DIR / 'junit.xml'}",
        *extra,
    ]
    log("running the tests")
    return subprocess.call(args, cwd="/e2e")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    command = argv.pop(0) if argv else "test"
    if command == "up":
        _up()
        return 0
    if command == "down":
        cluster.delete_cluster()
        return 0
    if command == "test":
        return _test(argv)
    if command == "shell":
        _up()
        os.execvp("bash", ["bash"])
    die(f"unknown command {command!r}, use test, up, down or shell")
    return 2


if __name__ == "__main__":
    sys.exit(main())
