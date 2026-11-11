"""Thin wrappers around the command line tools, and polling helpers."""
import subprocess
import sys
import time
from typing import Callable, Optional


class CommandError(RuntimeError):
    def __init__(self, cmd, result):
        self.cmd = cmd
        self.result = result
        super().__init__(
            f"command failed with exit code {result.returncode}: {' '.join(map(str, cmd))}\n"
            f"{(result.stdout or '').strip()}\n{(result.stderr or '').strip()}"
        )


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def run(*cmd, check: bool = True, input: Optional[str] = None, timeout: Optional[int] = 600, env=None):
    result = subprocess.run(
        [str(c) for c in cmd], capture_output=True, text=True, input=input, timeout=timeout, env=env
    )
    if check and result.returncode != 0:
        raise CommandError(cmd, result)
    return result


def docker(*args, **kw):
    return run("docker", *args, **kw)


def kind(*args, **kw):
    return run("kind", *args, **kw)


def kubectl(*args, **kw):
    return run("kubectl", *args, **kw)


def helm(*args, **kw):
    return run("helm", *args, **kw)


def apply(manifest: str, *extra: str) -> None:
    """kubectl apply of a YAML string."""
    kubectl("apply", *extra, "-f", "-", input=manifest)


def wait_until(
    check: Callable[[], object],
    timeout: float,
    interval: float = 2.0,
    message: str = "condition",
):
    """Polls check() until it returns a truthy value, which is returned. Exceptions count as not yet."""
    deadline = time.monotonic() + timeout
    last_error: Optional[BaseException] = None
    while True:
        try:
            value = check()
            if value:
                return value
        except Exception as error:  # noqa: BLE001
            last_error = error
        if time.monotonic() >= deadline:
            detail = f": {last_error}" if last_error else ""
            raise TimeoutError(f"timed out after {timeout:.0f}s waiting for {message}{detail}")
        time.sleep(interval)


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr, flush=True)
    sys.exit(1)
