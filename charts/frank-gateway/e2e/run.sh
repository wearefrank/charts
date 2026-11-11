#!/usr/bin/env sh
# Runs the end-to-end tests of the frank-gateway chart in a container. Needs only Docker.
#
#   ./run.sh                    create the cluster if needed and run all tests
#   ./run.sh test -k mtls       run the tests that match an expression, extra arguments go to pytest
#   ./run.sh up                 only create the cluster
#   ./run.sh down               delete the cluster
#   ./run.sh shell              open a shell in the runner, with kubectl and helm for the cluster
#
# Environment: E2E_KEEP=1 keeps the Helm releases of the tests for inspection,
# E2E_COMPONENTS installs only some components in the cluster (see fge2e/config.py), for example metallb,haproxy,
# E2E_KUBE_NODE_IMAGE selects another Kubernetes version, E2E_RESULTS_DIR is where logs and reports go.
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo=$(CDPATH= cd -- "$here/../../.." && pwd)
results=${E2E_RESULTS_DIR:-"$repo/e2e-results"}
image=${E2E_IMAGE:-frank-gateway-e2e}
mkdir -p "$results"

docker build --quiet --tag "$image" "$here" > /dev/null

tty=""
if [ -t 0 ] && [ -t 1 ]; then tty="-it"; fi

exec docker run --rm $tty \
  --name "frank-gateway-e2e-$$" \
  --cap-add NET_ADMIN \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume "$repo":/repo:ro \
  --volume "$results":/results \
  --env E2E_KEEP --env E2E_KUBE_NODE_IMAGE --env E2E_CLUSTER_NAME --env E2E_COMPONENTS \
  "$image" "$@"
