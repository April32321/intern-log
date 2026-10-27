FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git bzip2 procps less \
 && rm -rf /var/lib/apt/lists/*

ARG NODE_VERSION=22.20.0
ARG TARGETARCH
RUN case "$TARGETARCH" in \
      arm64) A=arm64 ;; \
      amd64) A=x64 ;; \
      *) echo "unsupported arch: $TARGETARCH" && exit 1 ;; \
    esac \
 && curl -fsSL "https://npmmirror.com/mirrors/node/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${A}.tar.gz" -o /tmp/node.tar.gz \
 && tar -xzf /tmp/node.tar.gz -C /usr/local --strip-components=1 \
 && rm /tmp/node.tar.gz && node -v && npm -v

RUN npm config set registry https://registry.npmmirror.com \
 && npm install -g @kilocode/cli \
 && npm cache clean --force

RUN useradd -m -s /bin/bash dev
USER dev
ENV HOME=/home/dev
WORKDIR /work
CMD ["bash"]
