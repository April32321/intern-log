---
day: 07
date: 2026-10-27
theme: Kilo 工作流与 Docker 心智模型
gate: -
---

# Day 07｜Kilo 工作流与 Docker 心智模型

## 今日目标

- 建立三类提示词模板（解释 / 执行 / 审查），后面 13 天反复用
- 让 Kilo 干一次真活，并抓它一次错、去官方页面核实
- 说清镜像 / 容器 / 卷 / 端口的对应关系
- 立住「YOLO 只准在容器里开」的边界，能讲清 `--auto` 与 `permission: allow` 的区别

## 今日完成

| 计划 | 状态 | 证据 |
|---|---|---|
| 三类提示词模板 | ✅ | `notes/kilo.md`「提示词模板（D7，贯穿 D7–D20）」，+43 行（`b9db4a6`） |
| 审查 `code/setup_check.sh` | ✅ | 必须改 2 条、建议改 4 条、可保留 4 条 + 采纳判断（`f77669b`） |
| 抓一次错并核实 | ✅ | 论文 DOI 记成 `10.1038/ncomms4006`，官方页面是 `10.1038/ncomms5006`（`f77669b`） |
| Docker 概念对照表 | ✅ | `notes/docker.md`：镜像 / 容器 / 卷 / 端口 / Dockerfile / registry 六行表（`5863274`） |
| 容器内 YOLO 小节 | ✅ | 三档权限表 + 兜得住 / 兜不住各 4 条 + 判断口诀 + 安全跑法逐行解读 |
| 四个问题 | ✅ | `notes/docker.md`「四个问题」，含 Conda vs Docker 对照表 |
| 文件名对齐验收 | ✅ | `notes/Docker.md` → `notes/docker.md`（`5863274`） |
| Docker 实操 | ⏸ 按计划在 D8 | 今天只做概念，未拉镜像、未 `docker run` |

## 关键命令

```bash
git mv notes/Docker.md notes/Docker.tmp
git mv notes/Docker.tmp notes/docker.md

git add notes/kilo.md
git commit -m "day07: 补三类提示词模板（解释/执行/审查）到 notes/kilo.md"

git add notes/kilo.md
git commit -m "day07: 补脚本评审与 TCIA 事实核查记录"

git add notes/docker.md
git commit -m "day07: docker 概念与容器内 YOLO 边界"
```

事实核查用的两个来源：

```text
https://www.cancerimagingarchive.net/collection/nsclc-radiomics/
https://api.crossref.org/works/10.1038/ncomms5006
https://api.crossref.org/works/10.1038/ncomms4006
```

## 卡点与认知

### 卡点 1：论文 DOI 差一位，`ncomms4006` 是另一篇文章

- **它说的**：TCIA NSCLC-Radiomics 422 例，数据集 DOI `10.7937/K9/TCIA.2015.PF0M9REI`，论文 DOI `10.1038/ncomms4006`。
- **官方页面**：422 subjects；数据集 DOI 同左（Version 4，2020/10/22，35.78 GB，1,265 series，52,073 images）；论文 DOI 是 **`10.1038/ncomms5006`**。
- **验证过程**：Crossref 查 `ncomms5006` → Aerts et al. 2014《Decoding tumour phenotype by noninvasive imaging using a quantitative radiomics approach》；查 `ncomms4006` → Ganter et al.《Predicting network functions with nested patterns》，与影像组学无关。
- **根因**：把"文章编号 4006"记成了 DOI 后缀；`ncomms5006` 与 `ncomms4006` 都格式合法、都能被 `doi.org` 解析，所以肉眼和链接都看不出错。
- **下次怎么避免**：引用 DOI 前先解析一次（`curl -sI https://doi.org/<doi>`），并核对返回的标题与作者。

### 卡点 2：`setup_check.sh` 两处静默 PASS

- **现象**：静态审查发现，缺 `git/conda/docker/kilo` 时脚本仍输出 `RESULT: PASS`；磁盘值取不到时 `avail=unknown` 会进 `[ "unknown" -lt 150 ]`，报错被 `if` 条件吞掉，同样 PASS。
- **根因**：`for` 循环只 `check ... MISSING`，不置 `fail`；磁盘检查只判 `-n`，没判数字。
- **处理**：写进评审记录，采纳这两条；按计划留到 D8 前改脚本，今天不混进 notes 的 commit。
- **下次怎么避免**：脚本的"结论行"必须由所有检查项共同决定，任何一个 `MISSING` 或"无法解析"都不能算 PASS。

### 认知 3：大小写改名要两步

macOS 文件系统大小写不敏感，直接把 `Docker.md` 改成 `docker.md`，路径看起来没变，git 也记不住这次改名。用 `Docker.tmp` 中转一次，提交里才会出现 `delete Docker.md` + `create docker.md`。

## 今日结论

1. 三类模板的分工是"先懂 → 先约 → 先审"：解释型不落盘，执行型先看 ≤10 步计划，审查型只许分三组、不许改文件。
2. 模型的事实性回答必须核查，"差一位的 DOI"比明显错误更危险；官方页面 + Crossref 双查能兜住。
3. Docker 的四件套是镜像（只读模板）、容器（可写实例）、挂载（唯一持久层）、端口（宿主:容器）；容器内一切临时，只有 `/work` 活着。
4. `--auto` 是执行方式，`permission: allow` 是权限边界；YOLO = 两者叠加，只准在容器里开。
5. 容器兜得住"容器内删根、未挂载处乱写、资源吃满（部分）"，兜不住"删 `/work`、Key/数据外发、`git push`、磁盘与额度"。
6. 代码放宿主、环境放镜像：代码要改要 diff 要提交，环境要稳定要可重建，两者靠 bind mount 连接。

## 明日 3 件事

- [ ] 装 Docker（本机 Docker Desktop 或 t12ub Engine），`docker run --rm hello-world` 通过
- [ ] 跑 Ubuntu 容器 + `-v "$PWD":/work` 挂载验证，注意 `--user` 属主坑
- [ ] 在容器内装 Kilo CLI，配置 YOLO，build `kilo-box:0.1`（计划写 `ubuntu:22.04`，我在 Day07 页手写 24，开工前先确认版本）
