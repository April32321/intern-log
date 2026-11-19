# 简历「Research Experience」条目模板

> 与示例同结构：标题 + 时间 / 机构 + 导师 / Innovation Points / Workloads 1–3 / Results。
> 所有 `[方括号]` 为占位符；没有的内容整行删除，不要留空括号。
>
> 标签可替换：`Innovation Points` → `Objective` / `Research Question`；
> `Workloads` → `Contributions` / `Work`。结构与行数不变。

## 1. 英文模板（可直接复制到 Word）

```text
Research Experience

[Project Title]                                         [MM/YYYY–MM/YYYY]
[Project Type], [Institution / Company]                 Advisor: [Name]

Innovation Points: [One sentence stating the research question — "Investigated whether ..." —
without claiming novelty.]

Workloads:
  1. [Data & setup] [What you collected, processed, or built; tools; scale.]
  2. [Method & implementation] [What you developed, compared, or implemented; key parameters.]
  3. [Evaluation & validation] [Metrics, split protocol, statistical tests, robustness checks.]

Results: [Primary metric ± SD (n = [N]).] [Comparison or secondary metric.] [Key deliverable.]
[One honest sentence on scope or limitation.]
```

## 2. 中文模板

```text
研究经历

[项目标题]                                              [YYYY.MM–YYYY.MM]
[项目类型]，[学校 / 单位]                               导师：[姓名]

研究问题：[一句话说明"是否/能否……"，不写"创新性地提出"。]

主要工作：
  1. [数据与准备] [收集/处理/搭建了什么；工具；规模。]
  2. [方法与实现] [开发/比较/实现了什么；关键参数。]
  3. [评估与验证] [指标、划分方式、统计检验、稳健性检查。]

结果：[主指标 ± 标准差（n = [N]）。] [对比或次要指标。] [核心交付物。]
[一句如实说明范围或限制。]
```

## 3. 每一行写什么

| 位置 | 写什么 | 长度 | 注意 |
|---|---|---|---|
| 标题 | 项目名，名词短语或动名词开头 | ≤ 12 词 | 不加 "A Study of" 之类空话 |
| 时间 | `MM/YYYY–MM/YYYY`；进行中写 `Present` | — | 与简历其他条目格式一致 |
| 项目类型 | Undergraduate Research Project / Research Internship / Independent Project | — | 不要写成不存在的身份 |
| 机构 / 导师 | 学校或单位；导师姓名 | — | 没有导师就删掉右半边 |
| Innovation Points | 研究问题，不是"创新" | 1–2 行 | 复现类项目尤其避免"novel" |
| Workload 1 | 数据、环境、预处理 | 1–2 行 | 优先写规模、版本、可复现性 |
| Workload 2 | 方法、模型、系统 | 1–2 行 | 优先写关键参数与工程难点 |
| Workload 3 | 评估、统计、质控 | 1–2 行 | 写清指标与验证协议 |
| Results | 数字 → 对比 → 交付物 → 限制 | 3–4 行 | 先给最强证据，限制放最后 |

## 4. 填写规则

1. **每条以动词开头**：Built / Implemented / Developed / Processed / Extracted / Evaluated / Validated / Reproduced / Audited / Quantified / Automated。
2. **数字优先**：样本量、特征数、耗时、版本、指标值；没有数字的 bullet 通常可以删。
3. **只写做完的**：未完成的实验、待补的结果、TODO 不要进简历；宁可不写，也不留占位符。
4. **对比要同口径**：样本量、划分方式、指标定义一致才并列；否则只报单边结果。
5. **"提升"必须有对照**：没有 baseline 就不写 improved / outperformed。
6. **限制句只写一句**：放在 Results 末尾，说明范围（如 only one cohort）或复现级别（method-level），不要写成自我否定。
7. **一条经历 10–12 行**：3 条 Workloads + 4 行 Results，控制在一页内。
8. **时态**：已完成用过去时；仍在进行用现在时或现在完成时。

## 5. 句式库（无具体数据）

**研究问题**

- Investigated whether [X] improves / reproduces / generalizes to [Y].
- Tested whether [method] can recover [target] under [constraint].

**Workloads**

- Built [environment/pipeline] with [tool/version] and [validation].
- Processed [N] [units] from [source] into [deliverable].
- Implemented [method] under [key parameters], achieving [runtime/scale].
- Diagnosed [failure mode] and isolated it to [cause].

**Results**

- Achieved [metric] of [value] ± [SD] (n = [N]), compared with [baseline] of [value].
- Reduced [metric] by [X]% relative to [baseline].
- Produced [deliverable] with [quality check] across [N] [units].
- Identified [finding], which [implication].
- Because [constraint], the work is scoped as [scope], not [stronger claim].

## 6. 常见错误

| 错误 | 改法 |
|---|---|
| `Innovation Points` 写成"首次提出" | 改成研究问题；复现类项目写 "Investigated whether ..." |
| 写 "participated in / assisted with" | 写你具体做了什么、产出是什么 |
| 列工具清单（Python, Docker, ...） | 把工具放进动作句：`Built a Docker + Conda environment ...` |
| 结果只有形容词（"效果良好"） | 换成指标 + 数值 + 样本量 |
| 把 apparent 和 CV 并列 | 分行标注口径与 n |
| 写论文的外部验证数字 | 没有对应队列就不写 |
| 一段超过 15 行 | 删到 3 条 Workloads + 4 行 Results |

## 7. 排版（对齐示例）

- 标题加粗，时间右对齐（Word 用右对齐制表位，不要敲空格）。
- 机构行斜体，导师右对齐。
- `Innovation Points:` / `Workloads:` / `Results:` 加粗，冒号后接正文。
- Workloads 用 1. 2. 3. 编号，不用项目符号。
- 字号、行距与简历其他 section 一致；整段不超过一页的 1/3。

## 8. 提交前检查

- [ ] 没有占位符残留（`[ ]`、`X.XX`、`TODO`）。
- [ ] 所有数字都能在日志/结果文件里找到出处。
- [ ] 没有把"方法级复现"写成"数值级复现"。
- [ ] 没有外部验证队列却写了外部 C-index。
- [ ] 导师/单位/时间真实。
- [ ] 每条 bullet 都能用一句话回答"这体现了什么能力"。
