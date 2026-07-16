FROM quay.io/dystewar/hermes:latest

USER 0

ARG K8SGPT_VERSION=v0.4.36
ARG TARGETARCH

RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) ARCH=x86_64 ;; \
      arm64) ARCH=arm64 ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}"; exit 1 ;; \
    esac; \
    curl -L \
      "https://github.com/k8sgpt-ai/k8sgpt/releases/download/${K8SGPT_VERSION}/k8sgpt_Linux_${ARCH}.tar.gz" \
      | tar -xz; \
    install -m0755 k8sgpt /usr/local/bin/k8sgpt; \
    rm -f k8sgpt

COPY . /opt/hermes/plugins/k8sgpt

RUN chgrp -R 0 /opt/hermes/plugins/k8sgpt && \
    chmod -R g=u /opt/hermes/plugins/k8sgpt

ENV K8SGPT_BIN=/usr/local/bin/k8sgpt

USER 1001