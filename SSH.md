# SSH

Secure Shell，加密的网络协议，用于安全地远程登录和传输数据。

## 常用用法

- `ssh user@host` 远程登录
- `ssh-keygen -t rsa` 生成密钥对
- `ssh-copy-id user@host` 上传公钥实现免密登录
- `scp file user@host:/path` 远程复制文件
- `~/.ssh/config` 配置主机别名
- 默认端口 22，密钥存放于 `~/.ssh/`
