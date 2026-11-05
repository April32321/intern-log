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

## 11. 本项目完整分析流程

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

---

## 12. 必背公式总结

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

## 13. 最重要的结论

1. **Event** 决定研究什么事件，本项目以死亡为终点。
2. **Survival Time** 衡量从治疗开始到死亡或随访结束的时间。
3. **Right Censoring** 表示未观察到死亡，但仍然知道患者已经存活的时间。
4. **Survival Function** 描述存活超过某个时间点的概率。
5. **Hazard Function** 描述已经存活到某个时间点时的瞬时死亡风险率。
6. **Kaplan–Meier** 通过各事件时间点的条件生存比例连乘，估计生存曲线。
7. **Log-rank Test** 比较不同组的整体生存分布。
8. **Median Survival Time** 是 KM 曲线第一次达到或低于 0.5 的时间；如果始终未达到，则报告 Not Reached。

**核心理解：生存分析的关键在于同时考虑事件发生时间和删失信息，从而合理估计患者的生存情况。**
