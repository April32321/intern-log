---
day: 08
date: 2026-10-28
theme: Docker 实操（Ubuntu 容器内装 Kilo + 自建镜像）
gate: -
---

# Day 08｜Docker 实操：Ubuntu 容器内装 Kilo、自建镜像

## 今日目标

- 装好 Docker Desktop，`hello-world` 通过
- 在本机 Ubuntu 24.04 容器里从零装好 Kilo，完成授权和冒烟
- 在容器内开 YOLO，确认写文件不再逐条批准，且结果落到宿主
- 把"容器内装 Kilo"固化成 `kilo-box:0.1` 镜像

## 今日完成

| 计划 | 状态 | 证据 |
|---|---|---|
| 装 Docker | ✅ | Docker Desktop 4.97.0；`docker run --rm hello-world` 输出 `Hello from Docker!`（arm64v8） |
| 拉 Ubuntu 镜像 | ✅ | `ubuntu:24.04` → `PRETTY_NAME="Ubuntu 24.04.5 LTS"` |
| 处理 Docker Hub 超时 | ✅ | 配 `docker.m.daocloud.io` + `docker.1ms.run` 镜像源，两者 `/v2/` 返回 401 |
| 容器内装 Node + Kilo | ✅ | 容器内 `node v22.20.0`、`npm 10.9.3`、`kilo 7.8.18` |
| 授权 + 冒烟 | ✅ | `kilo auth login` 选 DeepSeek；`kilo run --auto ... "只回复 KILO_OK"` |
| 容器内 YOLO | ✅ | `permission: allow` 后写 `/work/logs/yolo-ok.txt`，无批准提示，输出 `DONE` |
| 挂载双向 + 属主 | ✅ | 容器 `uid=1001(dev)` 写入，宿主显示 `501:20`；`YOLO_OK` 可读 |
| 数据集只读挂载 | ✅ | `/data:ro` 可读 `LUNG1-001/308`；`touch` 报 `Read-only file system`，`exit=1`（`logs/day08-ro-mount.txt`） |
| 固化镜像 | ✅ | `kilo-box:0.1` 1.01GB；`--rm` 运行 `kilo --version` → `7.8.18`（`logs/day08-kilo-version.txt`） |
| 清理临时容器 | ✅ | `docker rm -f kilo-box`，`docker ps -a` 无残留 |
| `intern-base:0.1` | ✅ | `docker build -t intern-base:0.1 -f env/Dockerfile .` 成功（8/8）；默认 `uid=1001(dev)`、`HOME=/home/dev`、`User=dev`；git 2.43.0 / Python 3.12.3（`logs/day08-intern-base.txt`） |
| 项目 `env/Dockerfile` v0 | ✅ | Ubuntu 24.04 + 常用 CLI + 非 root `dev`；D16 再升 v1 |
| `intern-base` 加固 v0.1 | ✅ | 基础镜像钉 digest（`ubuntu@sha256:24737cef…`）；`DEBIAN_FRONTEND` 由 `ENV` 改 `ARG`，运行时 `Config.Env` 无该项；`git config --system --add safe.directory=*`（容器内输出 `*`）；`.dockerignore` 补 `.env`；重建后 `Created=2026-10-28T07:01:18Z` |

## 关键命令

```bash
# 宿主：镜像源（Docker Desktop → Settings → Docker Engine）
# { "registry-mirrors": ["https://docker.m.daocloud.io", "https://docker.1ms.run"] }

docker pull ubuntu:24.04
mkdir -p ~/work/yolo-sandbox/logs && cd ~/work/yolo-sandbox
docker run -it --name kilo-box -v "$PWD":/work -w /work ubuntu:24.04 bash
```

```bash
# 容器内 root
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl git bzip2 procps less
useradd -m -s /bin/bash dev
su - dev
```

```bash
# 容器内 dev
curl -fSLO https://npmmirror.com/mirrors/node/v22.20.0/node-v22.20.0-linux-arm64.tar.gz
tar -xzf node-v22.20.0-linux-arm64.tar.gz
mkdir -p ~/.local && mv node-v22.20.0-linux-arm64 ~/.local/node
export PATH="$HOME/.local/node/bin:$PATH"
npm config set registry https://registry.npmmirror.com
npm install -g @kilocode/cli
kilo auth login
kilo run --auto -m deepseek/deepseek-flash "只回复 KILO_OK"
```

```bash
# YOLO 配置 + 验证
mkdir -p ~/.config/kilo
cat > ~/.config/kilo/kilo.jsonc <<'EOF'
{
  "$schema": "https://app.kilo.ai/config.json",
  "permission": "allow"
}
EOF
kilo run --auto -m deepseek/deepseek-flash \
  "执行 bash 命令：echo YOLO_OK > /work/logs/yolo-ok.txt。完成后只回复 DONE"
```

```bash
# 镜像
#docker build -t kilo-box:0.1 -f env/kilo-box.Dockerfile .
#docker run --rm -it --user dev -e HOME=/home/dev \
#  -v ~/work/yolo-sandbox:/work -w /work kilo-box:0.1 kilo --version
```

```bash
# intern-base:0.1（D8 补做）
docker build -t intern-base:0.1 -f env/Dockerfile .
docker run --rm intern-base:0.1 id
# uid=1001(dev) gid=1001(dev) groups=1001(dev)
```

```bash
# 数据集只读挂载（data/raw 是 D4 的 2 例冒烟数据）
docker run --rm -u dev -e HOME=/home/dev \
  -v "$PWD/data/raw:/data:ro" \
  kilo-box:0.1 bash -lc \
  'ls /data/lung1_smoke && touch /data/should-fail.txt; echo "touch exit=$?"'
# LUNG1-001 / LUNG1-308
# touch: cannot touch ... Read-only file system
# touch exit=1

docker run --rm -u dev -e HOME=/home/dev \
  -v "$PWD":/work -w /work \
  -v "$PWD/data/raw:/data:ro" \
  kilo-box:0.1 bash -lc \
  'touch /work/logs/ro-test.txt && echo WRITE_OK; touch /data/x.txt 2>/dev/null || echo DATA_READONLY'
# WRITE_OK / DATA_READONLY
```

```bash
# 停止容器
docker stop kilo
docker ps -a
# 删除容器
docker rm kilo
docker ps -a
# 列出本机镜像
docker images
#删除该镜像
docker rmi kilo-box:0.1
```

```bash
# docker run --rm -it --user dev -e HOME=/home/dev \
#   -v ~/work/yolo-sandbox:/work -w /work kilo-box:0.1 kilo --version

#镜像起一个常驻容器
docker run -itd --init \
  -v $PWD/work/input:/input:ro \
  -v $PWD/work/output:/output:rw \
  --name kilo \
  --hostname kilo \
  kilo-box:0.1 \
  sleep infinity
```

## 知识点：只读挂载（`:ro`）

`-v 宿主路径:容器路径:ro` = 把宿主目录挂进容器，但**容器只能读，不能写**。

| 挂载方式 | 容器能读 | 容器能写 | 对宿主的影响 |
|---|---|---|---|
| `-v "$PWD/data/raw:/data"` | ✅ | ✅ | 容器里的删改会真的落到宿主 |
| `-v "$PWD/data/raw:/data:ro"` | ✅ | ❌ `Read-only file system` | 容器改不动；宿主自己仍可改 |

实测（`logs/day08-ro-mount.txt`）：

- `ls /data/lung1_smoke` 正常列出 `LUNG1-001`、`LUNG1-308`
- `touch /data/should-fail.txt` → `Read-only file system`，`touch exit=1`
- 同一容器内 `/work` 可写 → `WRITE_OK`，`/data` 不可写 → `DATA_READONLY`

要点：

1. **只约束容器，不约束宿主**：Mac 上照常能改 `data/raw`；只读是容器这一侧的视图。
2. **保护不可再生的原始数据**：数据挂 `:ro`，代码和输出挂可写。YOLO 误删时 `/work` 会中招，`/data` 不会。
3. **只挡写，不挡读**：容器仍能读取全部数据并联网外发；防外发要靠 `--network none`。
4. **按挂载点生效**：别把同一个宿主目录再用可写方式挂到另一个路径，否则只读形同虚设。

一句话：`:ro` 是给容器的只读光盘——数据留在宿主，容器只能看、不能动。

## 知识点：`docker commit`

一句话：`docker commit` 把**容器当前的可写层**打包成一个新镜像，相当于给"正在跑的环境"拍快照。

```bash
docker commit [选项] <容器名或ID> <仓库:标签>
```

| 选项 | 作用 |
|---|---|
| `-m "说明"` | 提交信息，类似 git commit message，会写进 `docker history` 的 COMMENT |
| `-a "作者"` | 记录作者 |
| `-p` | 提交前暂停容器，避免文件写到一半（默认 `true`） |
| `-c 'CMD ["bash"]'` | 追加 Dockerfile 式指令修正配置（CMD / ENV / EXPOSE / USER / WORKDIR） |

### 实测（2026-10-28）

```bash
docker run --name ct -e FOO=bar ubuntu:24.04 bash -lc \
  'echo hi > /tmp/added.txt; mkdir -p /tmp/d; rm /etc/hostname'
docker diff ct
# C /tmp
# A /tmp/added.txt
# A /tmp/d

docker commit -m "commit 测试" ct commit-test:tmp
docker image inspect commit-test:tmp --format \
  'Cmd={{json .Config.Cmd}} Env={{json .Config.Env}} WorkingDir={{.Config.WorkingDir}}'
# Cmd=["bash","-lc","echo hi > /tmp/added.txt; mkdir -p /tmp/d; rm /etc/hostname"]
# Env=["FOO=bar","PATH=/usr/local/sbin:..."]
# WorkingDir=

docker run --rm commit-test:tmp bash -lc 'cat /tmp/added.txt'
# hi
```

### 它记录了什么

1. **只记录可写层的文件变化**：`docker diff` 里的 `A`（新增）/ `C`（修改）/ `D`（删除）。基础镜像层不变，新镜像 = 原层 + 一层 commit（本次 16.4kB）。
2. **容器的运行配置会一起写进镜像 `Config`**：启动命令 `Cmd`、`Entrypoint`、`docker run -e` 注入的环境变量、`WorkingDir`。
   - 实测 `Cmd` 变成了 `["bash","-lc", ...]`，`Env` 里多出 `FOO=bar`
   - 所以用交互式 `bash` 起的容器，commit 出来的镜像默认命令就是 `bash`，`docker run 新镜像` 会直接进 shell
3. **`--name`、`-p`、`-v`、`--rm` 不会进镜像**：它们属于宿主的容器运行配置。

### 它不记录什么 / 坑

| 坑 | 说明 |
|---|---|
| 挂载卷内容 | `-v` 挂进来的目录不在可写层，`/work`、`/data` 的改动**不会**进镜像；镜像里不含代码和数据 |
| 运行时伪文件 | `/etc/hostname`、`/etc/hosts`、`/etc/resolv.conf` 是运行时 bind mount，不在层里。实测容器内 `rm /etc/hostname` 后 `docker diff` 没有 `D` 记录 |
| 层只增不减 | `apt-get update` 的 lists、npm 缓存、后来删掉的文件都留在旧层里，镜像只会变大 |
| 历史不可见 | `docker history` 只有一条 commit + COMMENT，看不出中间装了什么 |
| 不可复现 | 没有配方，别人无法重建；基础镜像版本、步骤、顺序全部丢失 |
| 配置错位 | 容器的 `Cmd`/`Env` 会被继承，需要 `-c` 手工纠正，容易和预期不符 |

### 与 Dockerfile 的对比

| | `docker commit` | `docker build -f Dockerfile` |
|---|---|---|
| 来源 | 命令式，手工操作的历史 | 声明式文本配方 |
| 可复现 | ❌ 取决于你是否记得做过什么 | ✅ 可钉 digest（本项目 `env/Dockerfile:3`） |
| 可审计 | ❌ 只有一条 commit | ✅ 每层一条指令，`docker history` 一目了然 |
| 体积 | ❌ 易留垃圾，无法合并层 | ✅ 可用 `&& rm -rf` 合并层 |
| 改一行 | 重新手工操作再 commit | 改 Dockerfile 重建，缓存自动复用 |
| 适合 | 临时快照、调试取证 | 项目环境、交付、CI |

### 什么时候可以用

- 调试/取证：容器崩了、环境装到一半，先 `docker commit` 存现场。
- 临时抢救：手工调好的环境急着复用，先快照，事后补成 Dockerfile。
- 教学演示：直观展示"镜像分层 + 容器可写层"。

**对本项目的结论**：`intern-base`、`kilo-box` 这类环境一律走 `docker build`；`commit` 只当应急快照。手工步骤跑通后要抄回 `env/Dockerfile` 再重建，才能保住 README 要求的"可重建、可追溯"。

## 卡点与报错

### 卡点 1：Docker Hub 连不上，`context deadline exceeded`

- **报错原文**：
  ```text
  docker: Error response from daemon: failed to resolve reference
  "docker.io/library/hello-world:latest": failed to do request: Head
  "https://registry-1.docker.io/v2/library/hello-world/manifests/latest":
  context deadline exceeded
  ```
- **我的猜测**：镜像名写错，或者 Docker 没启动。
- **验证过程**：`docker version` 的 Client/Server 都有输出，排除引擎未启动；
  宿主 `curl https://registry-1.docker.io/v2/` 超时，`nc -vz registry-1.docker.io 443`
  也超时；DNS 能解析出地址。说明是 TCP 443 被阻断。
- **根因**：本机到 Docker Hub 的网络不通；Docker Desktop 的引擎跑在 Linux VM 里，
  macOS 系统代理不会自动传进去。
- **解决**：Docker Desktop → Docker Engine 加两个 registry mirror
  （`docker.m.daocloud.io`、`docker.1ms.run`），Apply & restart 后拉取成功。
- **下次怎么避免**：先 `curl <mirror>/v2/` 探测；返回 401 才是可用的 registry，
  返回 200 的要怀疑是网页。

### 卡点 2：GitHub raw 超时，nvm 装不上

- **现象**：`curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash`
  停在 0 字节，20 多秒无进展。
- **根因**：`raw.githubusercontent.com` 在本机不可达，nvm 的安装脚本拿不到。
- **解决**：不装 nvm，直接从 npmmirror 下载 Node 22 的二进制 tarball，
  解压到 `~/.local/node`，把 `bin` 加进 `PATH`；再用 `npmmirror` 的 npm registry 装 Kilo。
- **下次怎么避免**：凡是 `raw.githubusercontent.com` / `nodejs.org` 的安装脚本，
  先想好国内镜像的替代路径，不要等超时。

### 卡点 3：heredoc 结束符粘在别的命令后面

- **现象**：`EOF` 和 `docker run ...` 粘在同一行，提示符变成 `>`，文件没有生成。
- **根因**：heredoc 的结束符必须**单独一行且完全匹配**；`EOF docker run ...` 不等于 `EOF`，
  shell 继续等待输入，后面的命令全被当成文件内容。
- **解决**：`Ctrl-C` 取消，确认 `env/kilo-box.Dockerfile` 不存在后重写；
  或改用 `nano env/kilo-box.Dockerfile`。
- **下次怎么避免**：多行写入优先用编辑器；用 heredoc 时先确认最后一行只有 `EOF`。

### 卡点 4：`docker start` 后容器立刻 Exited

- **现象**：`docker start kilo-box` 后 `docker ps -a` 又显示 `Exited (0)`，
  `docker exec` 报容器没在运行。
- **根因**：这个容器的主进程是交互式 `bash`，`docker start` 是后台启动、没有 stdin，
  bash 读到 EOF 就退出。它是"一次性 shell 容器"，不是常驻服务。
- **解决**：`docker start -ai kilo-box` 附着进去；或改用镜像直接起 TUI：
  `docker run -it --user dev -e HOME=/home/dev ... kilo-box:0.1 kilo`。
- **下次怎么避免**：交互式容器用 `start -ai` / `attach`，服务型容器才用 `start`。

### 卡点 5：`docker exec -u dev` 的 HOME 仍是 `/root`

- **现象**：用 `-u dev` 进去后，预期能读到 `/home/dev/.config/kilo`，实际不会。
- **根因**：`-u` 只改 uid/gid，不改镜像里的 `HOME` 环境变量；ubuntu 基础镜像的
  `HOME` 是 `/root`，Kilo 于是去 `/root` 找配置和授权，YOLO 与登录都"失效"。
- **解决**：显式 `-e HOME=/home/dev`；进容器先 `echo $HOME` 验证。
- **下次怎么避免**：非 root 运行容器时，`--user` 和 `HOME` 必须成对出现。

### 卡点 6：挂载 Desktop 目录弹 macOS 隐私授权

- **现象**：执行 `-v "$PWD/data/raw:/data:ro"` 时，macOS 弹窗
  “Docker would like to access files in your Desktop folder”，终端命令挂起等待。
- **根因**：项目在 `~/Desktop/实习日志`，Docker Desktop 的 Linux VM 读取宿主文件
  需要 macOS 的"文件与文件夹"授权；系统代理或终端权限都不覆盖这一层。
- **解决**：点 **Allow**；误点 Don't Allow 时去
  `系统设置 → 隐私与安全性 → 文件与文件夹 → Docker` 勾选"桌面文件夹"。
- **下次怎么避免**：大数据/仓库尽量放 `~/work` 这类默认共享目录，少碰 Desktop；
  挂载后先 `ls /data` 确认不是空目录。

## 今日结论

1. 容器内装 Kilo 的真实依赖链是：apt 基础工具 → Node 22 → npm 全局包 → 交互式授权；
   缺任何一环都会以"command not found"或 401 的形式出现。
2. 国内网络下，Docker Hub、GitHub raw、nodejs.org 三个源都可能断；
   registry mirror + npmmirror tarball + npmmirror registry 是这次跑通的三件套。
3. YOLO 生效的判据不是"它说开了"，而是**写文件没有批准提示 + 宿主能看到落盘**。
4. `--user` 不等于 `HOME`；容器里"非 root"要同时满足 uid 和家目录，否则配置全部错位。
5. 交互式容器不是服务：`start` 会因没有 stdin 退出，要用 `start -ai` 或让主进程常驻。
6. 镜像是可复现的边界：`kilo-box:0.1` 只含工具，不含 Key、配置和代码；
   新容器重新授权是设计，不是缺陷。
7. `:ro` 只挡"写"，不挡"读"：容器仍能读数据、能联网外发；要防外发必须配合
   `--network none`，只读挂载解决的是"误删/误改"，不是"泄密"。

## 明日 3 件事

- [x] 补 D8 剩余：`intern-base:0.1` 与 `env/Dockerfile` v0
- [ ] 读 `每日计划/Day09.md`，装 Miniconda、建 `radiomics`（Python 3.10）环境
- [ ] 导出 `environment.yml` / `conda-explicit.txt` / `pip-freeze.txt`，并做一次重建验证

## 验收对照（Day08）

- [x] `docker run --rm hello-world` 成功
- [x] 容器内写文件、宿主能读到（`yolo-ok.txt` / `from-image.txt`）
- [x] 数据集 `:ro` 只读挂载：可读、不可写（`logs/day08-ro-mount.txt`）
- [x] 容器内 `kilo --version` → `7.8.18`，冒烟返回 `KILO_OK`
- [x] `env/kilo-box.Dockerfile` build 成功，镜像内 `kilo --version` 正常
- [x] `docker build -t intern-base:0.1`（`env/Dockerfile` v0，非 root `dev`）
- [x] 镜像可复现：基础镜像钉 digest，运行时无 `DEBIAN_FRONTEND`，`safe.directory` 生效
- [x] 能解释 `-v`、`-w`、`--user`、`--rm`、`-e` 的作用
- [x] 能说清 Key 用 `-e` / `auth login` 传、不写进 Dockerfile
