# 基础镜像钉 digest 保证可复现；升级时改这里：
#   docker image inspect ubuntu:24.04 --format '{{json .RepoDigests}}'
FROM ubuntu:24.04@sha256:24737cef17f4e22b1977df7d9a05e77c4e28b7da5b8911f8d8ccda136bf3573c

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 只作用于安装层，不污染运行时环境
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl wget git \
      bzip2 xz-utils unzip zip \
      procps less nano python3 \
 && rm -rf /var/lib/apt/lists/* \
 && git config --system --add safe.directory '*'

ARG USERNAME=dev
ARG USER_UID=1001
ARG USER_GID=1001

RUN groupadd --gid "${USER_GID}" "${USERNAME}" \
 && useradd --uid "${USER_UID}" --gid "${USER_GID}" \
      --create-home --shell /bin/bash "${USERNAME}" \
 && mkdir -p /work \
 && chown "${USERNAME}:${USERNAME}" /work

USER ${USERNAME}
ENV HOME=/home/${USERNAME}
WORKDIR /work

CMD ["bash"]
