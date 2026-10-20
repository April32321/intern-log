# Docker

容器化平台，将应用及其依赖打包成可移植的容器。

## 核心概念

- **镜像 (Image)**：只读模板
- **容器 (Container)**：镜像的运行实例
- **仓库 (Registry)**：存放镜像，如 Docker Hub

## 常用命令

- `docker build -t name .` 构建镜像
- `docker run -d -p 8080:80 name` 运行容器
- `docker ps` 查看运行中的容器
- `docker images` 查看镜像
- `docker stop <id>` / `docker rm <id>` 停止 / 删除容器
- `docker pull` / `docker push` 拉取 / 推送镜像
