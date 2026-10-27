# Docker

容器化平台：把应用、依赖和一部分操作系统打包成镜像，在宿主内核上以隔离进程运行。本项目的定位是 **代码在宿主，环境在镜像**。

## 核心概念对照（D7）

| 概念 | 类比 | 命令 | 要点 |
|---|---|---|---|
| 镜像 image | 装好的系统盘（只读模板） | `docker images` | 分层、带 tag、不可变；容器从它启动 |
| 容器 container | 从模板启动的一台小机器 | `docker ps -a` | 在镜像上叠一层可写层；删容器 = 丢可写层 |
| 卷 volume / bind mount | 外挂硬盘（宿主与容器共享） | `-v $PWD:/work` | 双向；容器删了数据还在；bind mount 用宿主路径，volume 由 Docker 管理 |
| 网络 network / 端口 | 门牌号 | `-p 8888:8888` | 宿主端口:容器端口；不映射则宿主访问不到 |
| Dockerfile | 造系统盘的配方 | `docker build` | 一条指令一层；`COPY` 代码要放在依赖安装之后，才吃到缓存 |
| 仓库 registry | 系统盘商店 | `docker pull` / `docker push` | 本项目不推公开仓库，Key 不进镜像 |

**关键认知**：容器内一切皆临时，**只有挂载出去的东西活着**。容器删掉，`/` 下的改动全没；`/work` 里落盘的才是结果。

## 常用命令

- `docker build -t name .` 构建镜像
- `docker run -d -p 8080:80 name` 运行容器
- `docker ps` / `docker ps -a` 查看运行中 / 全部容器
- `docker images` 查看镜像
- `docker stop <id>` / `docker rm <id>` 停止 / 删除容器
- `docker pull` / `docker push` 拉取 / 推送镜像
- `docker exec -it <id> bash` 进容器
- `docker inspect <id>` 看挂载、网络、用户等实际配置
- `docker system df` 看镜像 / 容器 / 卷占用（磁盘满时先查这个）

## 容器内 YOLO 模式（D7 概念，D8 动手）

### 三档权限姿势

| 姿势 | 谁在把关 | 适合干什么 | 风险 |
|---|---|---|---|
| 宿主 TUI 逐条批准 | 我本人 | 改仓库代码、碰真实数据、`git push` | 低（但慢） |
| 容器内 TUI 逐条批准 | 我 + 容器边界 | D8 装 Kilo、跑通管线 | 低–中 |
| 容器内 YOLO（`permission: allow` + `--auto`） | 只剩容器边界 | 一次性试验、批量转换、试错脚本 | 中–高，**只准在容器里** |

### YOLO 是什么

YOLO = 一次把**全部**自动批准打开（读文件、写文件、写工作区外、删除、执行任意命令）。IDE 里是自动批准工具栏的总开关；CLI 里等价于把 `~/.config/kilo/kilo.jsonc` 的权限一次放开：

```jsonc
{
  "$schema": "https://app.kilo.ai/config.json",
  "permission": "allow"
}
```

### `--auto` 不等于 YOLO

- `permission` 决定**允许做什么**，是权限边界；`--auto` 决定**要不要停下来问人**，是执行方式。
- `kilo run --auto` 仍然遵守 `permission`：没被 allow 的操作在自治模式下**无人可问，直接拒绝**，不会自动放行。
- 所以"开了 `--auto`"≠"放开了权限"；只有 `permission: allow` + `--auto` 叠加，才是"无人值守 + 全权委托"。

### 为什么必须和 Docker 一起学

YOLO 拆掉"每次点批准"这道**人工闸门**；容器补上**另一道**闸门——文件系统与进程边界。两者互为前提："敢让它放手做"和"不怕它做错"必须同时成立，否则 YOLO 就是拿宿主机赌博。

```
宿主：git 闸门（先 commit、不挂 ~/.ssh、不配远端凭据）
└─ 容器：文件系统闸门（只挂 /work、--rm、非 root、cap-drop、资源限额）
   └─ YOLO：无闸门（permission: allow + --auto）
```

### 兜得住 vs 兜不住

| 事故 | 容器兜得住吗 | 靠什么 |
|---|---|---|
| 它 `rm -rf` 掉容器内 `/`、装坏系统库 | ✅ | 镜像不可变，`--rm` 后一条命令重建 |
| 它在没挂载的地方乱写、改 shell 配置 | ✅ | 容器内 `$HOME` 是它自己的，不是我的 |
| 它吃满内存 / CPU | ⚠️ 部分 | `--memory`、`--cpus`、`--pids-limit`；磁盘和 API 额度管不了 |
| 它删掉 `/work` 里的仓库文件 | ❌ | 挂载是双向的，只能靠先 `git commit` 兜 |
| 它把 Key / 数据发到外网 | ❌ | 只能靠 `--network none`、容器里不放 Key |
| 它 `git push`、改远端、动真数据 | ❌ | 别挂 `~/.ssh`、别在容器里配远端凭据 |
| 挂 `docker.sock`、`--privileged`、`-v /:/host` | ❌ 直接失守 | 等于把宿主交出去，任何理由都不做 |

- 兜得住（≥3）：容器内删根 / 装坏库、未挂载目录乱写、资源吃满（部分）。
- 兜不住（≥3）：删 `/work`、Key 与数据外发、`git push` 动真数据、磁盘与 API 额度。

### 判断口诀

**这活能不能"丢掉重跑、只看 `/work`、不碰 Key 和远端"？能 → 容器里开；不能 → 回宿主手动批准。结果永远只信 `/work` 里落了盘的东西，不信它的口头汇报。**

### 安全跑法（D8 build 出 `kilo-box:0.1` 后照抄）

```bash
docker run --rm -it --name kilo-yolo \
  --user "$(id -u):$(id -g)" \
  --cap-drop=ALL --security-opt=no-new-privileges \
  --pids-limit 512 --memory 4g --cpus 2 \
  -v "$PWD":/work -w /work \
  -e OPENAI_API_KEY="$KILO_KEY" \
  kilo-box:0.1 \
  bash -lc 'kilo run --auto -m <provider>/<model> "把 /work/data 里的 csv 转成 parquet 写到 /work/out，并打印行数"'
```

逐行读：

- `--rm` 用完即焚，**YOLO 的全部底气就在这**
- `--user "$(id -u):$(id -g)"` 不在容器里用 root，写出的文件属主是我
- `--cap-drop=ALL --security-opt=no-new-privileges` 收掉多余能力
- `--pids-limit / --memory / --cpus` 防它把机器跑死（磁盘和 API 额度另算）
- `-v "$PWD":/work` **只挂一个目录**
- `-e` 传 Key，不进镜像；纯离线试验再加 `--network none`
- 数据集目录可再叠一层只读：`-v "$PWD/../data":/data:ro`（D8 实测）

## Conda vs Docker

| 维度 | Conda | Docker |
|---|---|---|
| 隔离层级 | 进程 / 用户级 | 系统级 |
| 共享什么 | 宿主内核、libc、系统库、shell | 宿主内核（Mac 上是 Docker Desktop 的 Linux VM 内核） |
| 能换发行版吗 | 不能 | 能 |
| 管什么 | Python 解释器、包、PATH | 整个 rootfs：OS 包、系统库、工具链、服务 |
| 挡不住的 | glibc / 系统库 / 编译工具差异 | 内核漏洞、挂载目录、网络出口 |

本项目两者叠加：**Conda 管 Python 依赖，Docker 管整套系统环境**。

## 四个问题

### 1. 为什么本项目要用 Docker？"在我机器上能跑"的根因是什么

根因不是某一个包版本不同，而是**一整套隐式状态没被记录**：Python 版本、conda 通道、系统库（glibc、ITK 的编译依赖）、编译工具、locale、驱动。这些状态只存在于这台机器的历史里，换台机器就复现不出来。

本项目要在 Mac 和 Linux 服务器之间来回，还要让 20 天后的自己或别人重跑 DICOM → PyRadiomics → Cox。Docker 把 OS + 库 + 运行环境一起固化成镜像，宿主只剩内核和 `/work`，于是"环境"本身也能被版本化、被重建。

### 2. Conda 和 Docker 都在解决依赖，区别是什么

**隔离层级不同：进程级 vs 系统级**。conda 换掉 Python 和包，但仍在宿主的 libc 上跑；Docker 换掉整个用户空间，连发行版都能换。反过来说，Docker 不隔离内核——容器不是虚拟机（Mac 上那层 Linux VM 才是）。

### 3. 为什么容器内不要用 root 跑、不要往容器里存结果

- **不用 root**：容器内 uid 0 在 bind mount 上写出的文件，属主是宿主 root（Linux 上尤其明显），宿主上还得 `sudo` 才能删；一旦容器逃逸，逃出来的就是 root。`--user "$(id -u):$(id -g)"` 让写出的文件属主就是我。
- **不存结果**：容器可丢弃，`--rm` 一删可写层全没，镜像层也不该装运行产物。结果必须落在 bind mount（`/work`）里，才能"容器死了，结果还在"。
- 同理，Key 不写进镜像层（`docker history` 能看到），只用 `-e` 运行时注入。

### 4. 如果 YOLO 跑在宿主，最坏能怎样？容器兜住哪几条、兜不住哪几条

最坏：`rm -rf ~` 删掉仓库和文档、改坏 `~/.zshrc`、装坏系统库、读 `~/.ssh` 推到远端、把 Key 和数据发到外网、吃满磁盘。

- 容器兜住：
  1. 容器内 `rm -rf /`、装坏系统库 → 镜像不可变，`--rm` 重建。
  2. 在未挂载目录乱写、改 shell 配置 → 容器内 `$HOME` 与宿主无关。
  3. 吃内存 / CPU → `--memory / --cpus / --pids-limit`（部分兜住）。
- 容器兜不住：
  1. 删 `/work` 里的仓库文件 → 挂载双向，只能靠 git。
  2. Key / 数据外发 → 必须 `--network none`、容器里不放 Key。
  3. `git push`、动真数据 → 不挂 `~/.ssh`、不配远端凭据。
  4. 磁盘与 API 额度 → 不归容器管。

## 为什么代码放宿主、环境放镜像

- 代码要改、要 review、要提交，必须在我能直接编辑和 `git diff` 的地方；塞进镜像就得每次 rebuild，diff 也不直观。
- 环境要稳定、要可重建，才放进镜像；它变化慢，适合做层缓存。
- 两者用 bind mount 连接：镜像提供"能跑"，`/work` 提供"改什么、产出什么"。容器随时可弃，代码和结果都留在宿主。

## D8 待办（今天只立概念）

- 本机拉 Ubuntu 24 基础镜像，在容器内装 Kilo 并配置 YOLO。
- build `kilo-box:0.1`，照抄上面的安全跑法跑一次。
- 数据集目录以只读方式挂载（`:ro`）实测一次。
