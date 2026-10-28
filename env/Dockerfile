# env/Dockerfile — intern-base:0.1
# 项目通用基础镜像：Ubuntu 24.04 + 常用 CLI + 非 root 用户 dev
# 不包含：授权 Key、项目代码、数据、Conda 环境

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl wget git \
      bzip2 xz-utils unzip zip \
      procps less nano python3 \
 && rm -rf /var/lib/apt/lists/*

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
