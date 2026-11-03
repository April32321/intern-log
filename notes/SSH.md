# SSH

Secure Shell，加密的网络协议，用于安全地远程登录和传输数据。

## 常用用法

- `ssh user@host` 远程登录
- `ssh-keygen -t rsa` 生成密钥对（推荐 `-t ed25519`）
- `ssh-copy-id user@host` 上传公钥实现免密登录
- `scp file user@host:/path` 远程复制文件
- `~/.ssh/config` 配置主机别名
- 默认端口 22，密钥存放于 `~/.ssh/`
- GitHub 的 SSH 地址格式为 `git@github.com:用户名/仓库.git`
- `ssh -T git@github.com` 测试 SSH 认证是否可用

## 公钥与私钥

```
~/.ssh/id_ed25519       私钥，绝不能外传
~/.ssh/id_ed25519.pub   公钥，可以随便给
```

认证流程：服务器用**公钥**出题，客户端用**私钥**对挑战数据签名，服务器验签通过即放行。**私钥永远不出本机**，网络上传输的只有签名。

## ssh-agent 与 agent 转发

`ssh-agent` 是后台进程，负责保管解密后的私钥并代为签名。

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519   # macOS，passphrase 存钥匙串
ssh-add -l                                       # 列出 agent 里的 key 指纹
```

**agent 转发**解决"A 机有私钥、B 机有网络"的情况：转发的是 **agent 的 socket**（`$SSH_AUTH_SOCK`），不是私钥文件。B 机上的 git 想签名时，请求经 SSH 隧道回到 A 机的 agent 完成签名。

```bash
ssh -A host                      # 一次性开启转发
```

```
Host host
  ForwardAgent yes               # 或写进 config 长期开启
  ServerAliveInterval 30         # 每 30 秒发探测包，防 NAT 空闲回收
  ServerAliveCountMax 3
  TCPKeepAlive yes
```

验证转发是否生效（在远端执行）：

```bash
echo $SSH_AUTH_SOCK     # 必须非空，形如 /tmp/ssh-XXXX/agent.NNNN
ssh-add -l              # 应看到本机的 key 指纹（即使远端没有该私钥文件）
```

| 现象 | 原因 | 处理 |
|---|---|---|
| `$SSH_AUTH_SOCK` 为空 | 没用 `-A` 或 config 未生效 | `ssh -v host` 搜 `Requesting authentication agent forwarding` |
| 远端 `ssh-add -l` 报 `Could not open a connection` | 同上 | 同上 |
| `Remote: No agent forwarding` | 服务器 `AllowAgentForwarding no` | 改用 deploy key |
| tmux 里转发失效 | tmux 保留的是重连前的旧 socket 路径 | 重新导出 socket，或在 tmux 外 push |

**安全提醒**：转发期间，服务器上有权的人可以借用你的签名能力（不是拿到私钥文件），能操作你**所有**用该 key 的仓库。共享机器上优先用 deploy key（只对单个仓库有写权限）。

## 断线与长任务

- `client_loop: send disconnect: Broken pipe` = 客户端发现连接已死（空闲超时/网络抖动）
- 长任务（`conda env create`、训练、数据处理）必须放进 `tmux`：

```bash
tmux new -s work      # 新建会话
# Ctrl+b 然后 d      # 脱离，进程继续跑
tmux attach -t work   # 重新进入
tmux ls               # 列出会话
```

## 排错：连接被断 vs 认证失败

| 报错 | 阶段 | 含义 |
|---|---|---|
| `Connection closed` / `kex_exchange_identification` | 密钥交换前 | 链路被干预（端口封锁、防火墙重置），与密钥无关 |
| `Permission denied (publickey)` | 公钥鉴权 | 网络通了，但没有可用的私钥 |

- GitHub 22 端口常被封，可改走 443：`ssh -T -p 443 git@ssh.github.com`，config 里 `HostName ssh.github.com` + `Port 443`
- `nc` 显示成功不代表可达：DNS 返回 `198.18.0.0/15` 时说明是网关 fake-IP 透明代理，TCP 只是连到了本地代理
- macOS 的 `nc` 用 `-G` 设连接超时，Linux（OpenBSD netcat）用 `-w`

## 实例：两台机器互相配置 SSH 别名（t12ub ↔ pvmed190）

目标：在 t12ub 上直接 `ssh pvmed190`，在 pvmed190 上直接 `ssh t12ub`，不必每次敲 `-p`、`-i` 和完整用户名。

### 现状与前提

| 项 | t12ub | pvmed190 |
|---|---|---|
| 地址 | `192.168.18.87` | `192.168.1.190` |
| 端口 | `10022` | `3225` |
| 用户 | `jqw`（home `/home/jqw`） | `jiaqiwang`（home `/home/jiaqiwang`） |
| 本机对应私钥 | `~/Desktop/jqw/id_rsa` | `~/Desktop/jiaqiwang_190_key/id_ed25519` |

三个前提：

1. 两台在**不同的 /24 网段**，Mac 能同时访问不代表它们互通，先测：
   ```bash
   ssh t12ub    'nc -vz -w 3 192.168.1.190 3225'
   ssh pvmed190 'nc -vz -w 3 192.168.18.87 10022'
   ```
2. 两端的 `~` 各指自己的 home，config 里写 `~/.ssh/...` 会自动落到正确位置；**Mac 的 `/Users/...` 路径不能原样拷过去**。
3. 190 的私钥和 GitHub 的私钥都叫 `id_ed25519`，传过去必须**改名**，否则撞名覆盖。

### 1. t12ub 侧的 config

目标文件 `/home/jqw/.ssh/config`：

```sshconfig
Host pvmed190
    HostName 192.168.1.190
    Port 3225
    User jiaqiwang
    IdentityFile ~/.ssh/id_ed25519_pvmed190
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

> 远端不需要写 `Host t12ub` 指回自己：经公网 IP/端口回连自己常被 hairpin NAT 挡住，只会制造困惑。

### 2. pvmed190 侧的 config

目标文件 `/home/jiaqiwang/.ssh/config`：

```sshconfig
Host t12ub
    HostName 192.168.18.87
    Port 10022
    User jqw
    IdentityFile ~/.ssh/id_rsa_t12ub
    IdentitiesOnly yes
    ServerAliveInterval 60
```

### 两种写入方式

**方式 A：登录到远端用 vim 改**

```bash
ssh t12ub
vim ~/.ssh/config
```

**方式 B：全程留在本机执行（推荐）**

```bash
cat > /tmp/config.t12ub <<'EOF'
Host pvmed190
    HostName 192.168.1.190
    Port 3225
    User jiaqiwang
    IdentityFile ~/.ssh/id_ed25519_pvmed190
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF

rsync -avP --backup --suffix=.bak /tmp/config.t12ub t12ub:.ssh/config
ssh t12ub 'chmod 600 ~/.ssh/config'
```

方式 B 的三个动作分别是：`cat` 写**本机** `/tmp`、`rsync` 从本机推到远端、`ssh host '...'` 在**远端**执行 `chmod`。**不要先 `ssh` 进去再跑方式 B**，否则 `cat` 写到远端、`rsync t12ub:...` 变成远端连自己。

### 3. 传私钥并改权限

```bash
rsync -avP ~/Desktop/jiaqiwang_190_key/id_ed25519 t12ub:.ssh/id_ed25519_pvmed190
ssh t12ub 'chmod 600 ~/.ssh/id_ed25519_pvmed190'

rsync -avP ~/Desktop/jqw/id_rsa pvmed190:.ssh/id_rsa_t12ub
ssh pvmed190 'chmod 600 ~/.ssh/id_rsa_t12ub'
```

### 4. 补 known_hosts（最容易漏）

第一次从 190 连 t12ub 会报 `Host key verification failed.`：190 的 `known_hosts` 里没有 t12ub 的主机指纹，而 `BatchMode=yes` 又不允许交互确认。

最省事且安全的做法是复用 Mac 上**已经验证过**的指纹（格式恰好相同）：

```bash
grep '^\[192.168.18.87\]:10022 ' ~/.ssh/known_hosts | ssh pvmed190 'cat >> ~/.ssh/known_hosts'
ssh pvmed190 'chmod 600 ~/.ssh/known_hosts'
```

反向若 t12ub 不认识 190，同样从 Mac 搬 `[192.168.1.190]:3225` 的记录即可。

备选方案：交互式 `ssh -t pvmed190` 后执行 `ssh t12ub` 输入 `yes`；或临时用 `-o StrictHostKeyChecking=accept-new`（属于 TOFU，不如复用已验证指纹稳妥）。

### 5. 验收

```bash
ssh t12ub    'ssh -G pvmed190' | grep -Ei '^(hostname|port|user|identityfile|identitiesonly)'
ssh pvmed190 'ssh -G t12ub'    | grep -Ei '^(hostname|port|user|identityfile|identitiesonly)'

ssh t12ub    'ssh -o BatchMode=yes pvmed190 hostname'   # 期望 pvmed-190
ssh pvmed190 'ssh -o BatchMode=yes t12ub hostname'      # 期望 t12ub
```

两条都返回对端 hostname 即完成。

### 排错表

| 报错 | 阶段 | 处理 |
|---|---|---|
| `Host key verification failed.` | 主机指纹 | 补 `known_hosts`（见第 4 步） |
| `no such identity: ~/.ssh/xxx` | 私钥缺失 | 重传私钥，确认文件名与 `IdentityFile` 一致 |
| `Permission denied (publickey)` | 公钥鉴权 | 对端 `authorized_keys` 缺少对应公钥，用 `ssh-copy-id` 或手动追加 |
| `Connection timed out` | 网络 | 两网段不互通，改用 `ProxyJump` |
| `Pseudo-terminal will not be allocated` | 仅警告 | 外层 ssh 加 `-T` |

### 经验

- `rsync -a` 会把**权限一起同步**，覆盖后必须 `chmod 600`；加 `--backup --suffix=.bak` 可自动保留旧文件。
- 客户端 `config` 是 644 不会阻止 ssh 工作（只有私钥权限过宽才会被拒），但收紧到 600 更规范。
- 私钥复制到别人的服务器有风险；长期做法是在各机 `ssh-keygen` 生成**专用 key**，把公钥追加到对端 `authorized_keys`。
- 两台内网不通时别在远端折腾，直接在 Mac 上配跳板：`Host xxx` + `ProxyJump t12ub`。

### 回滚

```bash
ssh t12ub    'mv ~/.ssh/config.bak ~/.ssh/config'
ssh pvmed190 'mv ~/.ssh/config.bak ~/.ssh/config'
```

> GitHub 相关条目（`Host git` / `Host github.com`）本次暂未部署对应私钥，远端暂时用不了 GitHub；需要时再传 `~/.ssh/id_ed25519`，并跑一次 `ssh -T git@github.com` 记录主机指纹。
