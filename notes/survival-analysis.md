# Survival Analysis — 核心知识笔记

## 1. Survival Analysis（生存分析）

**定义：** 生存分析是一类研究事件发生时间（Time-to-Event）的统计方法。

生存分析主要关注两个问题：
- **事件是否发生（Event）**
- **事件什么时候发生（Survival Time）**

与普通统计分析不同，生存分析可以处理未观察到事件发生的患者，即删失数据（Censored Data）。

**本项目研究目标：** 分析患者从治疗开始到死亡或随访结束的生存情况，生存时间单位为天（days）。

---

## 2. Event（事件）⭐⭐⭐

**定义：** Event 是研究中关注的特定结果，例如死亡、疾病复发或肿瘤发生。

本项目规定：
- `deadstatus.event = 1`：死亡事件发生。
- `deadstatus.event = 0`：未观察到死亡事件，通常按右删失处理（需确认数据编码）。

事件指示变量：

\[
\delta_i =
\begin{cases}
1, & \text{观察到死亡事件}\\
0, & \text{右删失}
\end{cases}
\]

**重点：** Event = 0 不代表患者永远不会死亡，只表示观察期内没有记录到死亡事件。

教材位置：Chapter 2, Section 2.1, PDF 第 1 页。

---

## 3. Survival Time（生存时间）⭐⭐⭐

**定义：** Survival Time 是从研究起始时间到目标事件发生的时间。

本项目：
- 起始时间：治疗开始。
- 目标事件：死亡。
- 时间单位：天（days）。

设：
- \(T\)：真实的事件发生时间。
- \(C\)：删失时间。
- \(Y\)：实际观察到的时间。

则：

\[
Y=\min(T,C)
\]

事件指示变量：

\[
\delta=I(T\le C)
\]

两种情况：

1. **Event = 1：** 观察到患者死亡，记录死亡时间。
2. **Event = 0：** 患者在观察结束前未发生目标事件，只知道其真实生存时间晚于最后观察时间。

**重点：** 生存分析中的时间必须具有明确的起点、终点和单位。

教材位置：Chapter 2, Section 2.1, PDF 第 1 页。

---

## 4. Right Censoring（右删失）⭐⭐⭐

**定义：** 在观察结束时没有观察到目标事件，只知道真实事件发生时间晚于最后观察时间。

例如：
- 患者 A：治疗后第 100 天死亡，Event = 1。
- 患者 B：治疗后第 150 天仍存活，随访结束，Event = 0。
- 患者 C：治疗后第 80 天死亡，Event = 1。

对于患者 B：

\[
T>150
\]

我们知道患者至少存活了 150 天，但不知道真实死亡时间。

常见右删失原因：
- 研究结束时患者仍存活。
- 患者中途失访。
- 患者退出研究。

**重点：**
- Right Censoring 不等于死亡。
- 删失患者仍然提供有效的随访信息。
- 不能将删失患者直接视为死亡患者。
- 不能简单删除所有删失患者。

**为什么重要？**

如果忽略删失，可能导致生存概率估计出现偏差。

Kaplan–Meier 方法能够在适当的删失假设下利用这些不完整的观察数据。

教材位置：Chapter 3, Section 3.2。上传的 PDF 第 42 页仅涉及第三章开头。

---

## 5. Survival Function（生存函数）⭐⭐⭐

**定义：** 生存函数表示事件发生时间晚于时间 \(t\) 的概率。

\[
S(t)=P(T>t)
\]

例如：

\[
S(100)=0.8
\]

表示患者治疗后存活超过 100 天的概率为 80%。

### 5.1 与 CDF 的关系

累积分布函数：

\[
F(t)=P(T\le t)
\]

因此：

\[
\boxed{S(t)=1-F(t)}
\]

### 5.2 与 PDF 的关系

对于连续随机变量：

\[
S(t)=\int_t^\infty f(u)\,du
\]

\[
\boxed{f(t)=-\frac{dS(t)}{dt}}
\]

### 5.3 基本性质

- \(0\le S(t)\le1\)
- \(S(t)\) 单调不增。
- 在本章的正生存时间模型中，\(S(0)=1\)。
- 对于有限事件时间几乎必然发生的模型，\(S(t)\to0\)，当 \(t\to\infty\)。

**重点：** 生存函数描述的是存活超过某一时间点的概率，而不是该时刻死亡的概率。

教材位置：Chapter 2, Section 2.2, PDF 第 2–7 页。

---

## 6. Hazard Function（风险函数）⭐⭐⭐

**定义：** 风险函数描述患者已经存活到时间 \(t\) 时，下一瞬间发生目标事件的风险率。

对于连续随机变量：

\[
\boxed{h(t)=\frac{f(t)}{S(t)}}
\]

也可以写成：

\[
h(t)=-\frac{d}{dt}\ln S(t)
\]

**重点：**
- Survival Function：存活超过时间 \(t\) 的概率。
- Hazard Function：已存活到时间 \(t\) 时的瞬时死亡风险率。
- Hazard Rate 不是普通概率，数值可以大于 1。

### 6.1 Cumulative Hazard Function（累积风险函数）

定义：

\[
H(t)=\int_0^t h(u)\,du
\]

与生存函数的关系：

\[
\boxed{H(t)=-\ln S(t)}
\]

\[
\boxed{S(t)=e^{-H(t)}}
\]

### 6.2 风险函数的常见形状

1. Constant Hazard：恒定风险。
2. Increasing Hazard：风险随时间增加。
3. Decreasing Hazard：风险随时间下降。
4. Bathtub-shaped Hazard：风险先下降、保持较低水平、再上升。
5. Hump-shaped Hazard：风险先上升后下降。

**重点：** 风险函数能够帮助研究者理解事件风险如何随时间变化。

教材位置：Chapter 2, Section 2.3, PDF 第 7–12 页。

---

## 7. Kaplan–Meier Estimator（KM 估计）⭐⭐⭐

**定义：** Kaplan–Meier 是一种非参数生存函数估计方法，能够利用包含右删失的数据估计生存概率。

### 7.1 KM 估计公式

\[
\boxed{
\hat S(t)=\prod_{t_i\le t}\left(1-\frac{d_i}{n_i}\right)
}
\]

其中：
- \(t_i\)：第 \(i\) 个不同的事件发生时间。
- \(d_i\)：在 \(t_i\) 时发生事件的人数。
- \(n_i\)：在 \(t_i\) 前仍处于风险集的人数。
- \(\hat S(t)\)：估计的生存概率。

### 7.2 核心计算逻辑

在每个事件时间点：

\[
P(\text{存活通过当前事件时间点})
=1-\frac{d_i}{n_i}
\]

将所有事件时间点的条件生存比例连乘：

\[
\hat S(t)=\prod_{t_i\le t}P_i
\]

### 7.3 删失如何影响 KM 曲线？

- **死亡发生时：** 生存曲线下降。
- **删失发生时：** 生存曲线不下降。
- **删失之后：** 患者不再计入后续风险集。

KM 生存曲线是一条单调不增的阶梯函数。

### 7.4 简单计算例子

假设有 5 位患者：

| 患者 | 时间（天） | Event |
|---|---:|---:|
| A | 2 | 1 |
| B | 4 | 0 |
| C | 5 | 1 |
| D | 7 | 1 |
| E | 9 | 0 |

第 2 天：

\[
\hat S(2)=1-\frac15=0.8
\]

第 4 天患者 B 被删失，曲线不下降。

第 5 天：

\[
\hat S(5)=0.8\left(1-\frac13\right)=0.533
\]

第 7 天：

\[
\hat S(7)=0.533\left(1-\frac12\right)\approx0.267
\]

第 9 天患者 E 被删失，曲线不下降。

**重点：** KM 估计的核心是条件生存概率连乘，而不是直接计算“存活人数 / 总人数”。

教材说明：KM 估计属于 Chapter 2 之外的后续非参数生存分析内容。

---

## 8. Log-rank Test（Log-rank 检验）⭐⭐⭐

**定义：** Log-rank Test 是用于比较两个或多个组的整体生存分布是否存在统计学差异的假设检验方法。

例如：
- Group A：接受治疗 A 的患者。
- Group B：接受治疗 B 的患者。

### 8.1 假设

原假设：

\[
H_0:\text{两组生存分布相同}
\]

备择假设：

\[
H_1:\text{两组生存分布不同}
\]

### 8.2 检验原理

在各个事件时间点，比较：
- Observed Events：实际观察到的事件数。
- Expected Events：原假设成立时的期望事件数。

将各时间点的信息综合，得到检验统计量和 p-value。

### 8.3 p-value 的解释

当显著性水平为 0.05：

- \(p<0.05\)：拒绝原假设，认为两组生存分布存在统计学差异。
- \(p\ge0.05\)：未能拒绝原假设，没有足够证据认为两组生存分布不同。

### 8.4 重点注意

- Log-rank 比较的是整体生存分布，而不是单个时间点。
- 通常与 Kaplan–Meier 曲线一起使用。
- p-value 不直接表示治疗效果大小。
- 当两组生存曲线明显交叉时，传统 log-rank 检验的效能可能下降。

教材说明：Log-rank Test 未在上传的 Chapter 2 中系统介绍。

---

## 9. Median Survival Time（中位生存时间）⭐⭐⭐

**定义：** 中位生存时间是生存概率下降到 50% 时对应的时间。

对于连续生存时间分布：

\[
\boxed{S(t_{\text{median}})=0.5}
\]

对于 KM 估计：

\[
\boxed{
\hat t_{\text{median}}=\inf\{t:\hat S(t)\le0.5\}
}
\]

即 KM 曲线第一次达到或低于 0.5 的时间。

### 9.1 例子

假设：

\[
\hat S(5)=0.533
\]

\[
\hat S(7)=0.267
\]

则：

\[
\boxed{\hat t_{\text{median}}=7\text{ days}}
\]

### 9.2 Median Survival Not Reached（中位生存时间未达到）

如果整个观察期间：

\[
\hat S(t)>0.5
\]

那么无法从当前 KM 曲线估计中位生存时间。

报告中应写：

**Median survival was not reached (NR).**

不能直接填写 0，也不能把最大随访时间当作中位生存时间。

**重点：** Median Survival Time 不等于 Mean Survival Time（平均生存时间）。

教材位置：Chapter 2, Section 2.4, PDF 第 13–14 页。

---

## 10. 常见参数模型（补充教材重点）

### 10.1 Exponential Distribution（指数分布）

生存函数：

\[
S(t)=e^{-\lambda t}
\]

风险函数：

\[
h(t)=\lambda
\]

平均生存时间：

\[
E(T)=\frac1\lambda
\]

中位生存时间：

\[
t_{\text{median}}=\frac{\ln2}{\lambda}
\]

**特点：** 风险率恒定，具有无记忆性（Memoryless Property）。

### 10.2 Weibull Distribution（威布尔分布）

生存函数：

\[
S(t)=e^{-\lambda t^\alpha}
\]

风险函数：

\[
h(t)=\alpha\lambda t^{\alpha-1}
\]

形状参数 \(\alpha\) 决定风险变化趋势：

- \(\alpha<1\)：风险率递减。
- \(\alpha=1\)：风险率恒定，为指数分布。
- \(\alpha>1\)：风险率递增。

教材位置：Chapter 2, Section 2.5。

---

## 11. Cox Proportional Hazards Model（Cox 比例风险模型）⭐⭐⭐

**定义：** Cox Proportional Hazards Model 是生存分析中常用的半参数回归模型（Semi-parametric Regression Model），用于研究协变量（Covariates）与事件发生风险之间的关系。Cox 模型可以在适当假设下处理右删失数据。

例如，在医学研究中，可以分析：
- 年龄是否与患者死亡风险有关。
- 肿瘤体积是否与死亡风险有关。
- 影像组学特征是否能够预测患者预后。
- 不同治疗方式是否与患者生存结局有关。

**与 Kaplan–Meier（KM）方法的区别：**

| 方法 | 主要作用 |
|---|---|
| Kaplan–Meier Estimator | 估计患者的生存概率，绘制生存曲线 |
| Log-rank Test | 比较不同组的整体生存分布 |
| Cox Regression | 研究多个协变量与瞬时事件风险之间的关系 |

教材位置：Chapter 2, Section 2.6 — Regression Models for Survival Data，教材第 48–49 页。

### 11.1 Cox 模型核心公式

Cox 模型定义为：

\[
\boxed{
h(t\mid X)=h_0(t)\exp(\beta_1X_1+\cdots+\beta_pX_p)
}
\]

也可以写成：

\[
h(t\mid X)=h_0(t)e^{\beta^\top X}
\]

其中：

| 符号 | 含义 |
|---|---|
| \(h(t\mid X)\) | 给定协变量时，在时间 \(t\) 的瞬时事件风险率 |
| \(h_0(t)\) | Baseline Hazard，基准风险函数 |
| \(X_1,\ldots,X_p\) | Covariates，协变量 |
| \(\beta_1,\ldots,\beta_p\) | Regression Coefficients，回归系数 |
| \(\exp(\cdot)\) | 指数函数 |

### 11.2 Baseline Hazard（基准风险）

\(h_0(t)\) 表示所有协变量取 0 时的风险函数。Cox 模型可以理解为：

\[
\boxed{
\text{Individual Hazard}
=
\text{Baseline Hazard}\times\text{Covariate Effect}
}
\]

其中：

\[
\text{Covariate Effect}=e^{\beta^\top X}
\]

**重点：**
- 基准风险函数可以随时间变化。
- Cox 模型不要求提前指定基准风险函数的具体形式。
- 指数函数保证预测的风险率非负。
- Cox 模型主要研究协变量对相对风险的影响。

教材对应：Section 2.6，公式 (2.6.3)。

### 11.3 Hazard Ratio（HR，风险比）

Hazard Ratio 用于比较两个不同协变量水平对应的瞬时风险率。对于单个协变量：

\[
h(t\mid X)=h_0(t)e^{\beta X}
\]

当 \(X\) 从 \(x\) 增加到 \(x+1\) 时：

\[
HR=\frac{h(t\mid x+1)}{h(t\mid x)}
\]

代入 Cox 公式：

\[
\begin{aligned}
HR
&=\frac{h_0(t)e^{\beta(x+1)}}{h_0(t)e^{\beta x}}\\
&=e^\beta
\end{aligned}
\]

因此：

\[
\boxed{HR=e^\beta}
\]

**解释：** 在其他协变量保持不变的情况下，某个协变量每增加 1 个单位，瞬时风险率变为原来的 \(e^\beta\) 倍。对于增加 \(\Delta X\) 个单位：

\[
HR=e^{\beta\Delta X}
\]

**HR 的解释：**

| HR | 含义 | 解释 |
|---|---|---|
| HR = 1 | 风险率不变 | 无相对风险变化 |
| HR > 1 | 风险率升高 | 与更高事件风险相关（危险因素） |
| HR < 1 | 风险率降低 | 与更低事件风险相关（保护因素） |

**注意：** HR > 1 和 HR < 1 常被描述为危险因素和保护因素，但统计关联不一定代表因果关系。

**计算例子：**

假设肿瘤体积的 Cox 回归系数为 \(\beta=0.2\)，则：

\[
HR=e^{0.2}\approx1.221
\]

即肿瘤体积每增加 1 个单位，瞬时死亡风险率约增加：

\[
(1.221-1)\times100\%=22.1\%
\]

如果 \(\beta=-0.3\)，则：

\[
HR=e^{-0.3}\approx0.741
\]

即每增加 1 个单位，瞬时死亡风险率约降低：

\[
(1-0.741)\times100\%=25.9\%
\]

**重点：**
- HR 描述瞬时风险率的相对变化。
- HR 不等于死亡概率。
- HR 不直接表示生存时间的变化比例。
- HR 的解释取决于协变量的单位和编码方式。

### 11.4 Proportional Hazards Assumption（PH 比例风险假设）

**定义：** 对于固定协变量水平的不同个体或组，其风险率之比不随时间变化。

假设患者 A 和 B 的风险函数分别为：

\[
h_A(t)=h_0(t)e^{\beta X_A}
\]

\[
h_B(t)=h_0(t)e^{\beta X_B}
\]

两者风险比为：

\[
\begin{aligned}
HR(t)
&=\frac{h_A(t)}{h_B(t)}\\
&=\frac{h_0(t)e^{\beta X_A}}{h_0(t)e^{\beta X_B}}\\
&=e^{\beta(X_A-X_B)}
\end{aligned}
\]

因此：

\[
\boxed{HR(t)=\text{Constant}}
\]

风险比不依赖时间 \(t\)。

**直观理解：**

| 时间 | Group A Hazard | Group B Hazard | HR (B/A) |
|---|---|---|---|
| Day 1 | 0.01 | 0.02 | 2 |
| Day 2 | 0.02 | 0.04 | 2 |
| Day 3 | 0.03 | 0.06 | 2 |

虽然两组风险率都随时间增加，但风险比始终为 2，因此符合 PH 假设。

**重要区别：**
- PH 假设不要求 Hazard Function 恒定。
- PH 假设要求不同固定协变量组之间的 Hazard Ratio 恒定。
- 风险率可以随时间增加、下降或发生其他变化。

**与 Survival Function 的关系：**

\[
S(t\mid X)=S_0(t)^{\exp(\beta^\top X)}
\]

两边取对数：

\[
\ln S(t\mid X)=e^{\beta^\top X}\ln S_0(t)
\]

进一步得到：

\[
\boxed{
\ln[-\ln S(t\mid X)]
=
\beta^\top X+\ln[-\ln S_0(t)]
}
\]

因此，不同固定协变量组的 \(\ln[-\ln S(t)]\) 曲线理论上应具有平行关系。这可以用于辅助检查 PH 假设。

教材对应：Section 2.6，公式 (2.6.4)、(2.6.6)、(2.6.7)，教材第 48–49 页。

### 11.5 Schoenfeld Residuals（Schoenfeld 残差检验）

Schoenfeld 残差检验是检查 Cox 模型 PH 假设的常用方法（该内容为实际建模补充，上传教材 Chapter 2 没有系统讲解其计算过程）。

**基本原理：** 比较事件发生时实际观察到的协变量值与根据模型和风险集计算的期望协变量值。如果 PH 假设成立，经过适当缩放的 Schoenfeld 残差不应表现出系统性的时间变化趋势。

**假设检验：**

原假设：

\[
H_0:\text{PH assumption holds}
\]

备择假设：

\[
H_1:\text{PH assumption is violated}
\]

通常使用显著性水平 \(\alpha=0.05\)：

| p-value | 解释 |
|---|---|
| \(p<0.05\) | 有证据表明可能违反 PH 假设 |
| \(p\ge0.05\) | 未发现足够证据拒绝 PH 假设 |

**注意：** p-value 大于或等于 0.05 不代表 PH 假设一定成立。

**Python 实现：**

```python
from lifelines import CoxPHFitter

cph = CoxPHFitter()

cph.fit(
    df,
    duration_col="time",
    event_col="event"
)

cph.print_summary()

cph.check_assumptions(
    df,
    p_value_threshold=0.05,
    show_plots=True
)
```

其中：
- `df`：包含生存时间、事件标记和协变量的数据集。
- `duration_col="time"`：生存时间列。
- `event_col="event"`：事件标记列。
- `p_value_threshold=0.05`：显著性阈值。
- `show_plots=True`：显示相关诊断图。

**重点：** 建立 Cox 模型后，应检查 PH 假设，并在报告中说明检查方法和结果。

### 11.6 如果 PH 假设不满足怎么办？

**① Stratified Cox Model（分层 Cox 模型）**

对于不满足 PH 假设的分类变量，可以考虑使用分层 Cox 模型：

\[
h(t\mid X,s)=h_{0s}(t)e^{\beta^\top X}
\]

其中：
- \(s\)：分层。
- \(h_{0s}(t)\)：第 \(s\) 层的基准风险函数。
- \(\beta\)：其他协变量的回归系数。

核心思想是允许不同分层具有不同的基准风险函数。例如按照疾病分期分层，让不同分期拥有不同的基准风险函数。

注意：
- 分层变量通常不再估计一个统一的 HR。
- 其他协变量仍需满足模型对应的假设。

**② Time-varying Effects（时变效应）**

如果协变量对风险的影响随时间变化，可以使用时变系数模型：

\[
h(t\mid X)=h_0(t)\exp[\beta(t)X]
\]

此时：

\[
\boxed{HR(t)=e^{\beta(t)}}
\]

风险比可以随时间变化。例如某种治疗在早期的保护作用较强，但后期逐渐减弱。

**注意：**
- Time-varying Covariate：协变量本身随时间变化。
- Time-varying Coefficient：协变量对风险的影响随时间变化。
- 两者不是同一个概念。

**③ Accelerated Failure Time Model（AFT 模型）**

AFT 模型是 Cox 模型之外的另一类生存回归模型，基本形式：

\[
\boxed{\ln T=\alpha+\beta^\top X+\sigma W}
\]

其中：
- \(T\)：生存时间。
- \(X\)：协变量。
- \(\beta\)：回归系数。
- \(W\)：误差项。

AFT 模型直接研究协变量如何改变生存时间的尺度。对于常见的 AFT 参数化形式：

\[
\boxed{TR=e^\beta}
\]

其中 TR 表示 Time Ratio（时间比）。例如 \(TR=1.5\) 表示对应协变量增加 1 个单位时，模型中的生存时间尺度变为原来的 1.5 倍。

**Cox 与 AFT 的区别：**

| | Cox Model | AFT Model |
|---|---|---|
| 研究重点 | 瞬时风险率 | 生存时间尺度 |
| 核心指标 | Hazard Ratio (HR) | Time Ratio (TR) |
| 主要解释 | 风险率增加或降低多少 | 时间尺度延长或缩短多少 |
| 常见假设 | Proportional Hazards | 指定的 AFT 分布及模型结构 |

AFT 不一定优于 Cox，需要根据数据和研究目标选择。

教材对应：Section 2.6，公式 (2.6.1)–(2.6.2)，教材第 46–48 页。

### 11.7 Cox Model 与 Kaplan–Meier 的关系

**Kaplan–Meier** 主要回答：患者在时间 \(t\) 之后仍然存活的概率是多少？

\[
S(t)=P(T>t)
\]

**Cox Regression** 主要回答：在控制其他协变量后，某个变量与患者死亡风险之间有什么关系？

\[
h(t\mid X)=h_0(t)e^{\beta^\top X}
\]

例如：
- KM：比较高风险组与低风险组的生存曲线。
- Log-rank：检验两组整体生存分布是否存在统计学差异。
- Cox：估计肿瘤体积、年龄等变量对应的 HR。

### 11.8 医学影像组学中的 Cox 模型

假设从患者 CT 影像中提取 Tumor Volume、Texture Entropy、Shape Sphericity，同时记录 Survival Time 与 Event，可建立 Cox 模型：

\[
h(t\mid X)
=
h_0(t)
\exp(
\beta_1X_{\text{volume}}
+\beta_2X_{\text{entropy}}
+\beta_3X_{\text{sphericity}}
)
\]

通过模型可以：
1. 估计不同影像特征对应的 HR。
2. 研究影像特征与死亡风险的关联。
3. 结合多个变量构建患者风险评分。
4. 检查 PH 假设。
5. 进一步评估模型的预测表现。

需要注意，影像组学特征数量较多时，应重视过拟合、特征筛选、模型验证及潜在混杂因素。

### 11.9 Cox 部分必背公式

| 知识点 | 公式 |
|---|---|
| Cox Model | \(h(t\mid X)=h_0(t)e^{\beta^\top X}\) |
| Hazard Ratio | \(HR=e^\beta\) |
| HR for \(\Delta X\) | \(HR=e^{\beta\Delta X}\) |
| PH Assumption | \(HR(t)=\text{Constant}\) |
| Conditional Survival | \(S(t\mid X)=S_0(t)^{e^{\beta^\top X}}\) |
| Log-log Survival | \(\ln[-\ln S(t\mid X)]=\beta^\top X+\ln[-\ln S_0(t)]\) |
| Stratified Cox | \(h(t\mid X,s)=h_{0s}(t)e^{\beta^\top X}\) |
| Time-varying Effect | \(h(t\mid X)=h_0(t)e^{\beta(t)X}\) |
| AFT Model | \(\ln T=\alpha+\beta^\top X+\sigma W\) |

### 11.10 Cox 部分最重要的结论

1. **Cox Proportional Hazards Model** 用于分析多个协变量与事件风险之间的关系。
2. **Hazard Ratio（HR）** 是 Cox 模型的核心解释指标：\(HR=e^\beta\)。
3. **HR > 1** 表示较高的瞬时事件风险率，**HR < 1** 表示较低的瞬时事件风险率。
4. **PH 假设** 要求不同固定协变量组的风险比不随时间变化，而不是要求风险率本身恒定。
5. **Schoenfeld Residuals** 可用于检查 PH 假设，通常结合 p-value 和诊断图判断。
6. **如果 PH 假设不满足**，可以考虑 Stratified Cox、Time-varying Effects 或 AFT Model。
7. **KM 与 Cox 的区别：** KM 主要估计生存概率；Cox 主要估计协变量与瞬时风险率之间的关系。

**一句话总结：** Cox 模型通过基准风险函数和协变量的指数效应建立生存回归模型，利用 Hazard Ratio 解释协变量与死亡风险之间的关系，并要求在标准模型中满足比例风险假设。

---

## 12. 本项目完整分析流程

**Step 1 — Define Event**

确定目标事件：

`deadstatus.event = 1` 表示死亡。

**Step 2 — Define Survival Time**

计算从治疗开始到死亡或随访结束的时间，单位为天。

**Step 3 — Identify Censoring**

区分死亡事件和右删失，确保删失数据正确编码。

**Step 4 — Kaplan–Meier Estimation**

使用 KM 方法估计生存函数：

\[
\hat S(t)=\prod_{t_i\le t}\left(1-\frac{d_i}{n_i}\right)
\]

**Step 5 — Plot Survival Curves**

绘制 KM 生存曲线，观察不同时间点的生存概率。

**Step 6 — Median Survival Time**

计算 KM 曲线首次达到或低于 0.5 的时间；若未达到，则报告 Not Reached。

**Step 7 — Log-rank Test**

如果需要比较不同患者组，使用 log-rank 检验分析整体生存分布差异。

**Step 8 — Cox Regression**

以临床变量（如 age、Gender、Histology、Stage）拟合 Cox 模型，输出 β、HR、95% CI 与 p，并用 Schoenfeld 残差检验 PH 假设。

---

## 13. 必背公式总结

| 概念 | 公式 |
|---|---|
| Survival Function | \(S(t)=P(T>t)\) |
| CDF Relationship | \(S(t)=1-F(t)\) |
| Probability Density | \(f(t)=-S'(t)\) |
| Hazard Function | \(h(t)=f(t)/S(t)\) |
| Cumulative Hazard | \(H(t)=\int_0^t h(u)du\) |
| Survival–Hazard Relationship | \(S(t)=e^{-H(t)}\) |
| Mean Survival Time | \(E(T)=\int_0^\infty S(t)dt\) |
| Mean Residual Life | \(mrl(t)=\frac{\int_t^\infty S(u)du}{S(t)}\) |
| Kaplan–Meier | \(\hat S(t)=\prod_{t_i\le t}(1-d_i/n_i)\) |
| Median Survival | \(\inf\{t:\hat S(t)\le0.5\}\) |
| Cox Model | \(h(t\mid X)=h_0(t)e^{\beta^\top X}\) |
| Hazard Ratio | \(HR=e^\beta\) |
| Conditional Survival | \(S(t\mid X)=S_0(t)^{e^{\beta^\top X}}\) |
| Stratified Cox | \(h(t\mid X,s)=h_{0s}(t)e^{\beta^\top X}\) |
| AFT Model | \(\ln T=\alpha+\beta^\top X+\sigma W\) |

## 14. 最重要的结论

1. **Event** 决定研究什么事件，本项目以死亡为终点。
2. **Survival Time** 衡量从治疗开始到死亡或随访结束的时间。
3. **Right Censoring** 表示未观察到死亡，但仍然知道患者已经存活的时间。
4. **Survival Function** 描述存活超过某个时间点的概率。
5. **Hazard Function** 描述已经存活到某个时间点时的瞬时死亡风险率。
6. **Kaplan–Meier** 通过各事件时间点的条件生存比例连乘，估计生存曲线。
7. **Log-rank Test** 比较不同组的整体生存分布。
8. **Median Survival Time** 是 KM 曲线第一次达到或低于 0.5 的时间；如果始终未达到，则报告 Not Reached。
9. **Cox Model** 通过 \(h(t\mid X)=h_0(t)e^{\beta^\top X}\) 建立协变量与瞬时风险率的关系，核心指标为 HR：\(HR=e^\beta\)。
10. **PH 假设** 要求风险比不随时间变化（不是风险率恒定），需用 Schoenfeld 残差检验并报告结论；不满足时改用分层 Cox、时依项或 AFT。
11. **KM/Log-rank 与 Cox 的分工：** KM 估计生存概率、log-rank 比较组间整体生存分布、Cox 在控制混杂后估计协变量的 HR。

**核心理解：生存分析的关键在于同时考虑事件发生时间和删失信息，从而合理估计患者的生存情况。**
