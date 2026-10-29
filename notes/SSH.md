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
