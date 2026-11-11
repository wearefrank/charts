# syntax=docker/dockerfile:1.7
#
# End-to-end test runner for the frank-gateway chart.
#
# Stages (build one with `--target`):
#   docker-cli  the docker CLI, copied into the next stage
#   tools       everything needed to create a kind cluster and talk to it: docker, kind, kubectl, helm
#   runner      tools plus the Python dependencies and the tests. This is the default target.
#
# The runner talks to the Docker daemon of the host through a mounted socket, creates the kind cluster
# there and joins the `kind` network, so it works the same on Linux, macOS and Windows with Docker Desktop.

ARG PYTHON_IMAGE=python:3.12-slim-bookworm
ARG DOCKER_CLI_IMAGE=docker:29-cli

FROM ${DOCKER_CLI_IMAGE} AS docker-cli

FROM ${PYTHON_IMAGE} AS tools
# TARGETARCH is set by BuildKit, amd64 and arm64 are supported
ARG TARGETARCH=amd64
ARG KUBECTL_VERSION=v1.37.2
ARG KIND_VERSION=v0.33.0
ARG HELM_VERSION=v4.3.1
ARG KUBECTL_SHA256_amd64=c04487523e7aa7d1493f7808174c899db93d7a9cf57531420cd76b9bd415f8f4
ARG KUBECTL_SHA256_arm64=fcc16f63186659d9722014b7e02d5fdd2d4e669cb8c0ab66365d7d3b8ba03509
ARG KIND_SHA256_amd64=aee6151561422756b764a4ae28e7f44cda5af5a9eead3cc9985112b1de8d8e0d
ARG KIND_SHA256_arm64=20022bee6cfcd5086cb7234d218e3454e6090022f2a8f55d1fa7fcf42c3867a2
ARG HELM_SHA256_amd64=0403a88ae20913d11b10a2467b50087721fea7581736da6b9d3992f5357fe54b
ARG HELM_SHA256_arm64=8cf8f66ecbc252ac8f7f06cca68aba88508ddfde3a6a34feb1678ad1694b4f88

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl iproute2 iputils-arping \
    && rm -rf /var/lib/apt/lists/*

COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker

RUN set -eux; \
    kubectl_sha="KUBECTL_SHA256_${TARGETARCH}"; kind_sha="KIND_SHA256_${TARGETARCH}"; helm_sha="HELM_SHA256_${TARGETARCH}"; \
    curl -fsSL -o /usr/local/bin/kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl"; \
    echo "$(eval echo \$${kubectl_sha})  /usr/local/bin/kubectl" | sha256sum -c -; \
    curl -fsSL -o /usr/local/bin/kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-${TARGETARCH}"; \
    echo "$(eval echo \$${kind_sha})  /usr/local/bin/kind" | sha256sum -c -; \
    curl -fsSL -o /tmp/helm.tgz "https://get.helm.sh/helm-${HELM_VERSION}-linux-${TARGETARCH}.tar.gz"; \
    echo "$(eval echo \$${helm_sha})  /tmp/helm.tgz" | sha256sum -c -; \
    tar -xzf /tmp/helm.tgz -C /tmp "linux-${TARGETARCH}/helm"; \
    mv "/tmp/linux-${TARGETARCH}/helm" /usr/local/bin/helm; \
    rm -rf /tmp/helm.tgz "/tmp/linux-${TARGETARCH}"; \
    chmod +x /usr/local/bin/kubectl /usr/local/bin/kind /usr/local/bin/helm; \
    kubectl version --client; kind version; helm version --short

FROM tools AS runner
WORKDIR /e2e
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The tests are copied, not mounted, so that Windows line endings in a checkout cannot break them.
# The chart itself is mounted at /repo when the container runs.
COPY . /e2e
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/e2e \
    CHART_DIR=/repo/charts/frank-gateway
ENTRYPOINT ["python", "-m", "fge2e"]
CMD ["test"]
