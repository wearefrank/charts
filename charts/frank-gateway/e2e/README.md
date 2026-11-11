# End-to-end tests of the frank-gateway chart

These tests install the chart on a real Kubernetes cluster (kind) and check what a unit test cannot: that the pod
runs with a read-only root filesystem, that traffic arrives through each way of exposing the gateway, and that the
gateway sees the client address, so allow lists work.

They test the chart and the cluster around it, with a released gateway image. What the gateway does by itself, such as
TLS, mTLS, the custom plugins and how it reads `X-Forwarded-For` or the PROXY protocol, is tested on the image in the
[frank-gateway repository](https://github.com/wearefrank/frank-gateway) (`tests/image-behaviour`). That repository
does not depend on this chart, so a gateway release never waits for it.

You only need **Docker**. The tests run in a container that creates the cluster through the Docker socket of your
machine, so they behave the same on Linux, macOS and Windows (Docker Desktop), and in CI.

## Running them

```shell
# Linux, macOS
./run.sh                      # create the cluster if needed, run all tests
./run.sh test -k mtls         # only the tests that match, extra arguments go to pytest
./run.sh test tests/test_loadbalancer.py
./run.sh up                   # only create the cluster
./run.sh down                 # delete the cluster
./run.sh shell                # a shell with kubectl and helm for the cluster
```

```powershell
# Windows (PowerShell 5.1 or 7)
.\run.ps1
.\run.ps1 test -k mtls
.\run.ps1 down
```

| Setting | Effect |
| --- | --- |
| `E2E_KEEP=1` | keep the Helm releases of the tests, to inspect them with `./run.sh shell` |
| `E2E_KUBE_NODE_IMAGE` | another Kubernetes version, for example `kindest/node:v1.34.11` |
| `E2E_CLUSTER_NAME` | another cluster name, `fg-e2e` by default |
| `E2E_COMPONENTS` | install only some components, a comma separated list of `metallb`, `bgp`, `haproxy`, `envoy-gateway` and `prometheus-crds`, or `none`. Everything is installed by default. See [Cluster configurations](#cluster-configurations). |
| `E2E_RESULTS_DIR` | where the report and logs go, `e2e-results` in the repository by default |

The first run takes about 15 minutes: it builds the image, pulls the cluster images and installs the components.
The cluster is kept, so a next run takes about 10 minutes, and a single test file less. Run `down` to start over.
The report is `e2e-results/junit.xml`. For every failed test `e2e-results/failures/` has the state of the
releases: resources, events, descriptions of the pods and the logs of the gateway.

The runner has the Docker socket of your machine, which is the same as root on it. Only run code that you trust.

## What is installed in the cluster

| Purpose | Component |
| --- | --- |
| Kubernetes | kind, one control plane and two workers, with its default CNI that enforces NetworkPolicy |
| `LoadBalancer` addresses | MetalLB v0.16, in layer 2 mode with addresses from the top of the `kind` Docker network, and in BGP mode with a pool of its own |
| BGP router | an FRR container in the `kind` network, that the MetalLB speakers set up BGP sessions with. The runner sends traffic for the BGP pool through it. |
| Ingress | HAProxy Technologies Kubernetes Ingress controller, which does TLS passthrough and PROXY protocol |
| Gateway API | Envoy Gateway, with `HTTPRoute` and `TLSRoute` |
| `ServiceMonitor` | only the CRD of the Prometheus Operator |

The versions are in `fge2e/config.py` and in the `Dockerfile`, which checks the downloads against a SHA-256.

## Cluster configurations

A local run installs everything, so every test can run. CI runs each cluster configuration as a job of its own, in
parallel (`.github/workflows/frank-gateway-e2e.yml`, on the latest Kubernetes minor version), and a job only installs the
components that its tests need. Components that another one needs are added by themselves, so `bgp` also installs MetalLB.

| Configuration | `E2E_COMPONENTS` | Tests |
| --- | --- | --- |
| core | `none` | `test_core.py` |
| operations | `metallb,prometheus-crds` | `test_operations.py` |
| loadbalancer-l2 | `metallb` | `test_loadbalancer.py` |
| loadbalancer-bgp | `bgp` | `test_loadbalancer_bgp.py` |
| ingress | `haproxy` | `test_ingress.py` |
| gateway-api | `envoy-gateway` | `test_gateway_api.py` |

To run one the way CI does, for example `E2E_COMPONENTS=haproxy ./run.sh test tests/test_ingress.py`. A test that needs a
component that is not installed fails, so give a configuration its tests, or install more components. When you add a
test file, add it to the configuration it belongs to, or give it a new one, in the matrix of the workflow.

## How the tests reach the cluster

The runner joins the `kind` Docker network, so it reaches the Kubernetes API, the nodes and the load balancer addresses
directly. It also adds a second source address to its network interface. The two addresses are the two clients of the
tests, so an allow list can let one in and keep the other out, without a second container.

## The tests

| File | What it checks |
| --- | --- |
| `test_core.py` | non-root, no capabilities, seccomp, read-only root filesystem and writable paths on a real kubelet; routes from `apisix.yaml`; a rollout on a change of the inline file; a reload of an existing ConfigMap without a restart |
| `test_operations.py` | an in-flight request survives the deletion of the pod; a rolling update drops no requests; the Control API is only reachable from allowed namespaces by NetworkPolicy and not exposed by any method; metrics and ServiceMonitor; diagnostic mode; an upgrade to all features and a rollback |
| `test_loadbalancer.py` | with MetalLB in layer 2 mode: external address; HTTP and HTTPS; the chart defaults for TLS versions and ciphers reach the gateway; the real client address and an allow list; the client address is lost with the default traffic policy; a valid client certificate is accepted and a missing one refused, so the certificates reach the gateway |
| `test_loadbalancer_bgp.py` | with MetalLB in BGP mode, through a router: the sessions are up; the address comes from the BGP pool; with `Local` only the node with the gateway announces it, and the announcement is withdrawn when the gateway is gone; HTTP and HTTPS; the real client address and an allow list; with `Cluster` every worker announces it and the client address is lost |
| `test_ingress.py` | TLS passthrough serves the certificate of the gateway; mTLS through the Ingress; the client address is lost without PROXY protocol and kept with it, so an allow list works; an Ingress that terminates TLS and X-Forwarded-For |
| `test_gateway_api.py` | routes are accepted; the chart uses `TLSRoute` `v1`; the Gateway terminates TLS for an `HTTPRoute` and the client address and allow list work; SNI routing, own certificate and mTLS through a `TLSRoute` |

## Writing a test

- `deployer.deploy(values=...)` installs the chart in a namespace of its own and `deployer.remove(release)` removes it.
  Use a module scoped fixture to share a release between tests. `deployer.base_values(...)` has values that suit a
  small cluster and routes that echo what the gateway knows about a request (see `fge2e/apisix.py`).
- `net.request(address, host=..., source_ip=..., client_cert=..., tls_min=..., ciphers=...)` sets the address, the SNI name,
  the Host header, the client address, the client certificate and the TLS parameters, and returns what was negotiated.
  Errors are returned, not raised, so a test can assert that a request is refused.
- `pki` has a CA, the server certificate and valid, untrusted and expired client certificates.
- Wait with `wait_until(...)`, not with `sleep`.
