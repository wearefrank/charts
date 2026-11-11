# Runs the end-to-end tests of the frank-gateway chart in a container. Needs only Docker.
# Works with Windows PowerShell 5.1 and PowerShell 7.
#
#   .\run.ps1                    create the cluster if needed and run all tests
#   .\run.ps1 test -k mtls       run the tests that match an expression, extra arguments go to pytest
#   .\run.ps1 up                 only create the cluster
#   .\run.ps1 down               delete the cluster
#   .\run.ps1 shell              open a shell in the runner, with kubectl and helm for the cluster
#
# Environment: E2E_KEEP=1 keeps the Helm releases of the tests for inspection,
# E2E_COMPONENTS installs only some components in the cluster (see fge2e/config.py), for example metallb,haproxy,
# E2E_KUBE_NODE_IMAGE selects another Kubernetes version, E2E_RESULTS_DIR is where logs and reports go.
$ErrorActionPreference = 'Stop'

$here = $PSScriptRoot
$repo = (Resolve-Path (Join-Path $here '..\..\..')).Path
$results = if ($env:E2E_RESULTS_DIR) { $env:E2E_RESULTS_DIR } else { Join-Path $repo 'e2e-results' }
$image = if ($env:E2E_IMAGE) { $env:E2E_IMAGE } else { 'frank-gateway-e2e' }
New-Item -ItemType Directory -Force $results | Out-Null

docker build --quiet --tag $image $here | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'docker build failed' }

$interactive = @()
if (-not [Console]::IsInputRedirected -and -not [Console]::IsOutputRedirected) { $interactive = @('-it') }

docker run --rm @interactive `
  --name "frank-gateway-e2e-$PID" `
  --cap-add NET_ADMIN `
  --volume /var/run/docker.sock:/var/run/docker.sock `
  --volume "${repo}:/repo:ro" `
  --volume "${results}:/results" `
  --env E2E_KEEP --env E2E_KUBE_NODE_IMAGE --env E2E_CLUSTER_NAME --env E2E_COMPONENTS `
  $image @args
exit $LASTEXITCODE
