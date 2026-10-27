---
day: 06
date: 2026-10-27
theme: Kilo 安装、配置、冒烟测试
gate: -
---

# Day 06｜Kilo Code 安装、配置、冒烟测试

## 今日目标

- `kilo` 可用，冒烟测试返回 `KILO_OK`
- 确认模型支持 tool calling
- 说清 Key 存在哪、为什么仓库里没有

## 今日完成

| 计划 | 状态 | 证据 |
|---|---|---|
| 安装 Kilo | ✅ | 安装目录 `/home/jqw/.npm-global/lib/node_modules/@kilocode`；`kilo --version` → `7.8.18`（`kilo-version.txt`） |
| 配置 API | ✅ | `kilo auth list` → Kilo Gateway (oauth) + DeepSeek (api)，共 2 条凭据 |
| 选择模型 | ✅ | `kilo models deepseek` → 选用 `deepseek/deepseek-flash` |
| 冒烟测试 | ✅ | t12ub `smoke-test.txt` 输出 `KILO_OK` |
| tool calling | ✅ | 让 Kilo 执行 `echo TOOL_OK`，命令实际执行并返回 `TOOL_OK` |
| 凭据自查 | ✅ | Key 在 `~/.local/share/kilo/auth.json`（600）；`history` 的 `sk-` 命中均为检查命令自身 |
| agents 权限 | ✅ | `kilo agent list`：`code` 可写；`plan` 仅能写 plans 文件；`ask` 全 deny |
| tmux 包裹 | ✅ | `logs/day06-tmux-ls.txt`：`kilo: 1 windows (created Tue Oct 27 11:05:39 2026) (attached)` |
| TUI 目录/模型证据 | ✅ | `logs/day06-tmux-status.txt`：`~/work/intern-jqw-nsclc-survival`、`Code · DeepSeek V4.1 Flash 1017`、`7.8.18` |

## 关键命令

```bash
kilo --version
kilo models deepseek
kilo run --auto -m deepseek/deepseek-flash "只回复 KILO_OK" | tee smoke-test.txt
kilo run --auto -m deepseek/deepseek-flash "用 bash 执行 echo TOOL_OK，然后只回复 TOOL_OK"
kilo auth list
kilo agent list
jq 'keys' ~/.local/share/kilo/auth.json
grep -oE 'sk-[A-Za-z0-9_-]{8,}' ~/.local/share/kilo/auth.json | wc -l
```

## 卡点与报错

### 卡点 1：模型 ID 多写 `kilo/`，报 Add credits

- **报错原文**：
  ```text
  Error: Add credits to continue, or switch to a free model
  ```
- **我的猜测**：账号没有额度，或者模型 ID 写错了。
- **验证过程**：`kilo models deepseek` 只列出 `deepseek/deepseek-flash` 和
  `deepseek/deepseek-v4-pro`，`deepseek-v4.1-flash-1017` 不在其中；
  `kilo auth list` 显示两套凭据：Kilo Gateway (oauth) 与 DeepSeek (api)。
- **根因**：`kilo/` 前缀走 Kilo Gateway，该 OAuth 账号没有额度；模型 ID 也不在可用列表。
- **解决**：改用 `deepseek/deepseek-flash`，走自己的 DeepSeek Key，返回 `KILO_OK`。
- **下次怎么避免**：模型 ID 从 `kilo models <provider>` 原样复制；先 `kilo auth list`
  确认请求走的是哪套凭据。

### 卡点 2：`grep ~/.config/kilo*` 查不到 Key

- **现象**：计划里的凭据检查命令没有输出，一度以为没有凭据文件。
- **验证过程**：`kilo auth list` 显示 `Credentials ~/.local/share/kilo/auth.json`；
  `jq 'keys'` 得到 `["deepseek","kilo"]`；`ls -l` 显示该文件权限 `-rw-------`。
- **根因**：`~/.config/kilo/` 只放配置（`kilo.jsonc`），凭据实际在 `~/.local/share/kilo/`。
- **解决**：用 `kilo auth list` 定位真实路径，再用 `grep -ril` / `jq 'keys'` 检查，
  全程不打印 Key 内容。
- **下次怎么避免**：先确认工具把凭据存在哪，再做检查，不按计划里的路径硬猜。

### 卡点 3：TUI 显示 7.8.17，`kilo --version` 却是 7.8.18

- **现象**：`kilo --version` 返回 `7.8.18`，但 tmux 里运行中的 TUI 状态栏显示
  `~/work/intern-jqw-nsclc-survival 7.8.17`；`tmux capture-pane` 抓到的也是 7.8.17。
- **我的猜测**：装了两份 Kilo，或者升级没有生效。
- **验证过程**：`which -a kilo` 只有 `/home/jqw/.npm-global/bin/kilo` 一个；
  `ls -l $(which kilo)` 显示符号链接更新于 10:28；
  `ps -eo pid,lstart,args | grep '[k]ilo'` 显示 TUI 进程启动于 10:27。
  重启 TUI 后状态栏变为 7.8.18。
- **根因**：TUI 在升级前启动，进程加载的是旧版 7.8.17；二进制在 10:28 被替换，
  已运行的进程不会热更新。
- **解决**：`tmux kill-session -t kilo` 后重新 `tmux new -s kilo` 启动，
  状态栏与 `kilo --version` 一致为 7.8.18。
- **下次怎么避免**：升级后重启正在运行的 TUI；版本号与冒烟证据在同一次会话生成。

## 今日结论

1. `deepseek/deepseek-flash` 在 Kilo 7.8.18 下能返回 `KILO_OK`，也能真正调用 bash（`TOOL_OK`）。
2. Key 只在 `~/.local/share/kilo/auth.json`（600），仓库与命令历史都没有。
3. `kilo/` 前缀走托管 Gateway，`deepseek/` 才走自己的 API Key；模型 ID 必须从
   `kilo models <provider>` 复制。
4. 写文件必须用可写 agent（`code`）；Plan/Ask 的 deny 由权限层执行，不是提示词提醒。

## 明日 3 件事

- [ ] 读 `每日计划/Day07.md`（Kilo 工作流 + Docker 概念）
- [ ] 写提示词模板库，补 `notes/kilo.md`
- [ ] 建 `notes/Docker.md` 上半
