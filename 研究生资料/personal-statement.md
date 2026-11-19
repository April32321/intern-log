# Personal Statement — Jiaqi Wang

> 用途：Data Science / Bioinformatics 硕士申请。英文主稿约 800 词，中文对照稿在下半部分。
> 数字与口径与 `研究生资料/resume-experience-filled.md`、`notes/report-brief.md` 保持一致；出处见 Part 3 表 2。
> `[方括号]` 为需本人替换的占位符（学校/项目名、研究方向偏好）。
> 全文限定：内部 5×10 交叉验证、399 例分析集、SD 不是 95% CI、方法级复现而非外部验证。

## Part 1. English Draft

Every patient with non-small-cell lung cancer (NSCLC) already receives a CT scan, so a quantitative signature read out of that routine image would be prognostic evidence at no extra cost. That is the promise of radiomics, and the reason I do not take it on trust: a number from an unpublished script, on a pipeline nobody else can rebuild, is not evidence yet. Applied mathematics taught me to turn a vague question into a model that can be tested and, if wrong, shown wrong. This project taught me the harder half of that lesson — reproducibility is itself part of the evidence. I am applying to [program name] to study high-dimensional modeling, survival and causal inference, and reproducible data engineering, so that I can move work like this from reconstructed to usable.

The project I will describe was my own initiative: I chose to re-run a published study because I wanted to know what its numbers depended on. It was a method-level reproduction of the CT-radiomics-to-Cox workflow of Aerts et al. (*Nature Communications*, 2014) on the open Lung1 cohort of 422 patients. The paper reported no Lung1 training C-index and published no Cox weights, so there was no target number to hit; the task was to rebuild the workflow and measure what signal it carries in a pre-specified analysis set of 399 patients and 352 events. That removed my last excuse to tune toward a number.

The first challenge was that the pipeline itself is fragile engineering. Every one of the 422 scans had to yield a mask and the same 537 features — 25 HU bins, no resampling, Coif1 wavelet — which meant compiling PyRadiomics 3.0.1 from source. Extraction then died repeatedly inside an 8 GB container. I suspected forking, then shared memory, then a leak, and small experiments killed each: a twelve-scan memory trace zigzagged instead of climbing. A `--chunk 10` run settled it — the first ten scans failed, the second ten succeeded — and a single-case probe found the cause: LUNG1-058, 297 slices and 151 MB, exceeds the limit on its own. On a 40-core server the cohort finished in 942.6 s, and five recomputed cases matched to zero relative difference.

The second challenge was a result that contradicted my intuition. Stage is among the most established prognostic factors in NSCLC, yet its hazard ratio was near 1 and the clinical model's C-index was 0.530 ± 0.026, an interval spanning 0.5. Recoding stage until the numbers looked right was the one repair I refused. I audited the encoding, confirmed the 399-patient distribution and the I/II versus IIIa/IIIb mapping, and looked at the survival curves rather than a single p-value: early and late curves crossed around 1000–1500 days, log-rank p = 0.532. The coefficient was not wrong — one proportional hazard ratio was averaging two opposite phases of risk. I kept the violation in the report and added a stratified sensitivity analysis. Distinguishing an implementation error from data that does not support a claim became the core judgment I took from this work.

The third challenge was building a result that could be overturned by its own evidence. I sealed the analysis set (399 patients, 352 events) and the folds (5 × 10, seed 42, 50 held-out folds) before running any model, and kept every filter, screen, scaling step and LASSO alpha choice inside the training fold. The imaging routes then tied: signature 0.581 ± 0.038, in-fold LASSO-Cox 0.583 ± 0.035, combined 0.581 ± 0.034. Those are fold-to-fold SDs over folds that share patients, not confidence intervals; a patient-level bootstrap (0.543–0.608 for the signature) answers a different question. Below them lay instability: LASSO kept 11.3 features per fold, range 2–42; 99 features were selected at least once, only one in over 80% of folds; and it kept just one signature feature, in 8% of folds, at the same C-index. The honest conclusion is not that some signature is best, but that radiomics carries signal while no feature set is stable.

Those episodes became one method: diagnose a failure by enumerating its layers, design one experiment that can falsify several hypotheses, fix the protocol before seeing results, and separate what the data say from what I conclude. When an Energy feature sat thirty times below the paper's value, I compared three conventions across all 422 cases and found a single shift to the paper's HU+1024 scale explained it (1.03×).

What I want next follows from that. I want to study small-sample, high-dimensional problems — survival and causal inference, stability of model selection, infrastructure that lets someone else rebuild a pipeline. As a data scientist I want to work where being right matters more than being impressive: medicine, finance, anywhere an overstated finding is paid for by someone else. My analytics and time-series work gave me the engineering side; this project gave me the discipline. Where CT scans are already in the record, the most valuable contribution is not another score but one someone else can recompute and trust.

*Word count: 830 (body text only, excluding this line; counted by the script in Part 3 §7)*

## Part 2. 中文对照稿

每位非小细胞肺癌（NSCLC）患者本来就要做 CT，如果从这张常规影像里能读出一个定量签名，就等于零额外成本地拿到一条预后证据。这是影像组学的承诺，也正是我不敢直接采信它的原因：一串由未公开脚本算出、跑在别人无法重建的管线上的数字，还不算证据。应用数学的训练教我把模糊的问题写成可检验的模型——错了就能被证明是错的；这个项目教会我的是更难的那一半：可复现性本身就是证据的一部分。我申请 [program name]，想系统学习高维建模、生存与因果推断，以及可复现的数据工程，把这类工作从"能重建"推进到"能用"。

要讲的这个项目是我自己发起的：我选择重跑一篇已发表的研究，是因为想知道它的数字到底依赖什么。这是对 Aerts 等（*Nature Communications*, 2014）CT 影像组学→Cox 流程的方法级复现，数据是公开的 Lung1 队列（422 例）。论文没有报告 Lung1 训练集 C-index，也没有公开 Cox 权重，所以不存在要对准的目标数值；任务是重建整条流程，测量它在预先指定的 399 例 / 352 事件分析集上携带多少信号。这一步拿掉了我向某个数字"凑"的最后借口。

第一个挑战是管线本身就很脆弱的工程。422 例扫描必须逐一产出掩膜，并得到同样的 537 个特征（25 HU 分箱、不重采样、Coif1 小波），为此要先把 PyRadiomics 3.0.1 从源码编译出来。随后提取在 8 GB 容器里反复崩溃。我先怀疑 fork，再怀疑共享内存，又怀疑内存泄漏，每个猜测都被一个小实验否掉：12 例的内存曲线呈锯齿状而非单调上升。真正定案的是 `--chunk 10` 对照——前 10 例全灭、后 10 例全成——再用单例探针找到原因：LUNG1-058 有 297 层、151 MB，单例就超出上限。换到 40 核服务器后，全量在 942.6 s 内完成，另抽 5 例复算，最大相对差为零。

第二个挑战来自与直觉相反的结果。分期是 NSCLC 中最成熟的预后因素之一，可它的 HR 接近 1，临床模型的 C-index 只有 0.530 ± 0.026，区间覆盖 0.5。把分期重新编码到数字好看为止，是我唯一拒绝的"修法"。我先审计编码，确认 399 例的分期分布与 I/II 对 IIIa/IIIb 的映射都正确，然后去看生存曲线而不是单一 p 值：早期与晚期曲线在约 1000–1500 天处交叉，log-rank p=0.532。系数没有算错——单一的比例风险 HR 把两个方向相反的风险阶段平均掉了。我把这条违反留在报告里，并补了分层敏感性分析。区分"实现错误"与"数据不支持某个结论"，成了我从这项工作带走的核心判断。

第三个挑战是让结果能够被它自己的证据推翻。跑模型之前，我先封定分析集（399 例 / 352 事件）与折划分（5 折 × 10 次、seed 42、50 个测试折），并把所有过滤、筛选、标准化和 LASSO 的 alpha 选择都锁在训练折内。结果三条影像路线打平：签名 0.581 ± 0.038，折内 LASSO-Cox 0.583 ± 0.035，联合模型 0.581 ± 0.034。这些是共享病人折之间的折间标准差，不是置信区间；病人层面 bootstrap（签名为 0.543–0.608）回答的是另一个问题。其下的不稳定更说明问题：LASSO 每折保留 11.3 个特征（范围 2–42），99 个特征至少入选一次、只有 1 个超过 80% 的折，四个签名特征中只保留了一个（8% 的折），性能却相当。诚实的结论不是"某个签名最好"，而是：影像确实携带信号，但没有哪一组特征稳定。

这些经历合成了一套方法：失败先分层枚举，设计一个能同时否定多个假说的实验，结果出现前定死口径，并区分数据说了什么与我要得出什么结论。当 Energy 特征只有论文值的三十分之一时，我没有删它，而是在全部 422 例上对照三种口径，发现统一到论文的 HU+1024 口径就能解释（1.03×）。

我的下一步由此而来。我想研究小样本、高维的问题——生存与因果推断、模型选择的稳定性，以及能让别人重建一条管线的研究基础设施。作为数据科学家，我希望在"正确"比"好看"更重要的地方工作：医疗、金融，以及任何夸大结论的代价由别人承担的场景。数据分析与时间序列的经历给了我工程那一面，这个项目给了我纪律那一面。CT 已经躺在病历里，最有价值的贡献不是再给出一个分数，而是一个别人能重新算出来、也愿意相信的分数。

## Part 3. 写作说明

### 1. 核心主张与段落证据映射

**贯穿全文的核心主张**：可复现性本身就是证据的一部分——诚实报告的负结果比好看的正结果更有信息量。

| 部分 | 内容 | 关键证据（可引用的数字） | 想证明的能力 |
|---|---|---|---|
| Motivation | 常规 CT → 零成本预后证据；不可复现的数字不算证据 | 引文定位为方法级复现的原因（论文无 Lung1 训练 C-index、未公开权重） | 问题意识、对证据标准的敏感度 |
| 挑战一：脆弱工程 | OOM 误判链 | 297 层 / 151 MB / 8 GB；`--chunk 10` 两段对照；942.6 s；5 例复算最大相对差 0 | 受控实验优于经验调参 |
| 挑战二：数据不支持直觉 | stage 的 HR≈1 | 临床 0.530 ± 0.026（区间含 0.5）；log-rank p=0.532；KM 在 1000–1500 天交叉；编码审计无错配 | 区分实现错误与数据不支持 |
| 挑战三：结论可被推翻 | 建模前封板 | 399 例 / 352 事件；5×10、seed 42、50 折；0.581 / 0.583 / 0.581 ± SD；11.3 [2–42]；99 个特征；仅 1 个 >80%；4 个签名特征仅 1 个入选（8%）；bootstrap 0.543–0.608 | 先定口径、性能稳健 ≠ 特征稳健 |
| 方法收束 | 四个固定动作 + Energy 三口径 | Energy 0.03× / 0.41× / 1.03×（422 例） | 把个案上升为方法 |
| Impact | 学术方向 + 职业方向 | 一句带过 Beiming 分析平台、CUHK 时间序列 | 领域匹配度与自我认知 |

### 2. 数字出处表

| 数字 | 出处 |
|---|---|
| 422 例队列；399 例分析集 / 352 events | `notes/report-brief.md` §一、§二；`results/tables/analysis_set.md` §3 |
| 537 特征/例；0 非有限值；25 HU / 不重采样 / Coif1 | `notes/report-brief.md` §一；`code/params.yaml` |
| PyRadiomics 3.0.1 源码编译、NumPy 1.26.4 | `研究生资料/resume-experience-filled.md` §1 工作 1 |
| 297 层 / 151 MB / 8 GB OOM；`--chunk 10`（10 例全灭 + 10 例全成）；12 例内存曲线锯齿；942.6 s；5 例最大相对差 0 | `journal/day17.md` §二.7（含 `journal/day17.md:330-359`）、`journal/day17.md:447-448`、`journal/day17.md:520-548` |
| 四模型 C-index 0.530 / 0.581 / 0.583 / 0.581 ± SD | `results/tables/perf.csv`、`journal/day19.md` §3.1 |
| 5×10、seed 42、50 测试折；训练折内筛选 | `results/tables/cv_design.md`、`journal/day19.md` §3.1 |
| LASSO 11.3 [2–42]、99 个特征、仅 1 个 >80%、4 签名特征仅 1 个（4/50 = 8%） | `journal/day19.md` §3.3、§3.4；`results/tables/selection_stability.csv` |
| 训练−测试 optimism 0.003 / 0.049 / 0.057（写作说明备查，正文未用） | `journal/day19.md` §3.1 |
| signature bootstrap 95% CI 0.543–0.608 | `notes/report-brief.md` §二 表 |
| clinical bootstrap CI 0.527 [0.495, 0.558] 含 0.5（正文只写"区间覆盖 0.5"） | `notes/report-brief.md` §二 表 |
| stage：log-rank p=0.532、KM 1000–1500 天交叉、编码审计无错配 | `report.md` §4.4；`journal/day14.md:255-262`；`journal/day19.md:299-316` |
| Energy 三口径 0.03× / 0.41× / 1.03× | `report.md` §5.4；`journal/day19.md:248-267` |
| 论文无 Lung1 训练 C-index、未公开 Cox 权重 | `notes/report-brief.md` §三；`notes/paper-aerts2014.md` |
| Beiming 分析平台、CUHK 时间序列研究（仅一句带过） | `研究生资料/cv-template.md` §Internship Experience、§Research Experience |

### 3. 压缩到 550 词（及更短）时删哪几句

指第 1 / 2 / 3 / 4 / 5 / 7 段（与英文稿一致；中文稿对应段落同位置）。当前 830 词，按下列顺序删，删完需重排过渡句；数字为实测省下的词数。

1. 第 2 段末句 "That removed my last excuse to tune toward a number."（10 词）——修辞，不是事实。
2. 第 3 段 "On a 40-core server the cohort finished in 942.6 s, and five recomputed cases matched to zero relative difference."（19 词）——工程收尾，可移到简历。
3. 第 4 段 "I kept the violation in the report and added a stratified sensitivity analysis."（13 词）——保留"数据不支持结论"的主线即可。
4. 第 6 段 Energy 三口径那句（32 词）整句可删——最"案例化"、最不"方法化"的一段。
5. 第 5 段 "a patient-level bootstrap (0.543–0.608 for the signature) answers a different question"（15 词）可删，但**必须保留** "not confidence intervals"（否则口径塌陷）。
6. 第 7 段 "As a data scientist I want to work where being right matters more than being impressive: medicine, finance, anywhere an overstated finding is paid for by someone else."（31 词）压成 "I want to work where being right matters more than being impressive, and where an overstated finding is paid for by someone else."（22 词）。
7. 第 1 段 "I am applying to [program name] to study high-dimensional modeling, survival and causal inference, and reproducible data engineering, so that I can move work like this from reconstructed to usable."（31 词）删掉后半句，省 12 词。

删 1–4（74 词）后剩 756 词；再删 5（15 词）剩 741 词，此时已触及 740 词下限，但仍高于 550 词。要到 550 词必须再砍约 190 词，按以下顺序：

8. 第 3 段把三条被否定假说的清单压成 "Small experiments killed each guess."（省 17 词）。
9. 第 5 段把 LASSO 不稳定性那句压成 "Below that, LASSO selected 99 different features across folds."（省 22 词）——但保留 11.3 与 2–42 更好，若项目对数字密度敏感再删。
10. 第 1 段与第 2 段合并、删掉 Aerts 引文的期刊名与年份（省 ~10 词）。
11. 第 7 段压到两句："As a data scientist I want to work where being right matters more than being impressive, and where an overstated finding is paid for by someone else." + 末尾"可重算、可信任的分数"一句（省 ~36 词）。
12. 第 3 段删掉 PyRadiomics 3.0.1 源码编译与 25 HU / Coif1 口径细节（省 ~25 词，但会削弱"可重建"的说服力，最后才动）。
13. 第 4 段把编码审计句压成 "I audited the encoding instead."（省 ~15 词）。
14. 第 5 段把"sealed the analysis set ... before running any model"的插入语压短（省 ~10 词）。

若继续压到 400 词，删掉挑战二整段（stage 故事），但**至少要保留** 399 例、5×10、0.581 ± 0.038、"not confidence intervals"、LASSO 11.3 [2–42] 与"影像携带信号、特征集不稳定"这组对照。

### 4. 若学校要求 SOP 与 Personal History Statement 分开

本稿是 **SOP 型**（研究问题 → 方法 → 未来方向）。拆分方式：

- **SOP**：保留第 1 段（末两句改写成项目介绍）、第 2–6 段的全部技术内容，以及第 7 段的学术方向部分。删掉"我为什么想做数据科学家 / 在哪些行业"的职业句，让论文位置给更具体的 [program name] 课程与 [advisor name] 方向（留占位符）。
- **Personal History Statement**：本稿**不能**直接改，需要新增原创内容（成长背景、选择应用数学的契机、对"诚实报告"这一价值的个人来源）。本稿可作素材的三处：自己做项目的动机（不是被分配的任务）、"不好看的数字不等于 bug"背后的个人性格、以及想把方法用于高风险决策场景的职业愿望。**不要**把技术细节搬到 PHS 里。

### 5. 占位符替换示例

| 占位符 | 偏生信方向 | 偏通用 DS 方向 |
|---|---|---|
| `[program name]` | "the M.S. in Bioinformatics at [university]" 或 "Biomedical Data Science" | "the M.S. in Data Science at [university]" |
| 第 1 段研究兴趣 | survival modeling and multimodal clinical data | statistical learning and model-selection stability |
| SOP 版第 7 段 | "I want to extend this to multimodal imaging and clinical records..." | "I want to work on small-sample high-dimensional inference and reproducibility infrastructure..." |
| 导师 | `[advisor name]`（只在 SOP 版出现；无则整句删，不留空括号） |

### 6. 其他经历的可扩写位置

- Beiming（社区治理分析平台）：可写在第 7 段"工程那一面"处，扩写成 2–4 句（Getis–Ord Gi*、K-Means 聚类、FP-Growth 关联规则、FastAPI + Docker 部署），用于体现端到端部署与可复现部署能力；数字见 `研究生资料/cv-template.md`。
- CUHK 时间序列（07/2026–09/2026）：可写成"在高方差时间序列里对比 AR(1)/ARX/AR(p) 并做滚动窗口稳健性检验"，用来呼应"样本小、噪声大时如何报告"，但**不要**引入 RMSE 改善数字（易被读成"improvement"）。
- 三门应用线性代数课设（医学文本检索、label propagation、PCA/SVD）：只在需要证明"线性代数→实际建模"的连贯性时用一句；不要写进本稿正文。

### 7. 投递前自查清单

**口径三件套（必须在正文中至少各出现一次，自然句而非脚注）**

- [x] 内部交叉验证 ≠ 外部验证（正文写 "a method-level reproduction"，全文无 "external validation"）
- [x] 折间 SD ≠ 95% CI（第 5 段明写 "fold-to-fold standard deviations ... not confidence intervals"；bootstrap 单独说明 "answers a different question"）
- [x] 399 例分析集 ≠ 422 例队列（第 2 段同时写出两个数并说明 399 是 "pre-specified analysis set"）

**禁止词（全文必须为零）**

- [x] `improved` / `improvement` / `outperformed` / `better`（形容词用法）/ `numerical reproduction` / `external validation`
- [x] `0.65` / `0.69`（论文外部队列数值）
- [x] 把 399 写成 "cohort" 或 "our cohort"（正文写 "Lung1 cohort of 422 patients" 与 "analysis set of 399 patients"）

**其他**

- [x] 方括号占位符只剩 `[program name]` 一处，需本人替换（本稿无导师/学校名占位符；若 SOP 版加导师句，按 §5 处理）。
- [x] 词数已用下方命令统计：**830**（写入英文稿末尾）。
- [x] 中英文两版数字逐一对照（0.581/0.583/0.581、11.3 [2–42]、99、1 个 >80%、8%、0.543–0.608、942.6 s、297 层 / 151 MB）。
- [ ] 若项目要求 "personal history statement"，按 §4 另写，不要复用本稿。
- [x] 英文稿控制在 740–860 词；超出时按 §3 压缩。

**词数统计命令**（在仓库根目录执行，取 Part 1 到 Part 2 之间的正文；英文稿内已注明 830 词）：

```bash
python3 - <<'PY'
import re, pathlib
t = pathlib.Path("研究生资料/personal-statement.md").read_text()
en = t.split("## Part 1. English Draft")[1].split("\n## Part 2.")[0]
en = re.sub(r"\*Word count:[^*]*\*", "", en)
print("words:", len(en.split()))
for w in ["improved","improvement","outperformed","better","numerical reproduction","external validation","0.65","0.69","95%"]:
    print(w, len(re.findall(w, en, re.I)))
PY
```
