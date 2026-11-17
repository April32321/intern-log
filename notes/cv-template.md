# Jiaqi Wang

Tel: +1 (626)-491-1103 | Email: jiaqi32321@gmail.com

> 由 `Jiaqi Wang_CV(2).pdf` 提取整理；Research Experience 已并入 `notes/resume-experience-filled.md` 的 NSCLC 条目（中英两版内容一致，此处取英文汇总版，按时间倒序置首）。方括号 `[ ]` 为可替换占位符。
>
> 导出：`pandoc` + `xelatex`，Times New Roman 10pt，0.6in 边距，US Letter，成品 `notes/cv.pdf`（2 页）。

## Education

**University of California Santa Barbara** — Santa Barbara, CA | 09/2023–09/2026

B.S. in Applied Mathematics | Overall GPA: 3.64/4.0

## Internship Experience

### Digital Systems Department, Beiming Software Co., Ltd | 01/2026–07/2026

*Position: Data Analyst · Mentor: Shengyu Wang & Huajiang Ying · Hybrid*

**Community Governance Intelligence Analysis Platform**

1. Participated in a data analytics project focused on grassroots community governance.
2. Translated community governance needs into three analytical tasks — spatial hotspot detection, temporal trend identification, and event association mining — transforming raw event records into interpretable insights for decision support.
3. Designed and implemented an integrated analytical framework combining Getis–Ord Gi* spatial hotspot analysis, K-Means time-series clustering, and FP-Growth association rule mining; classified areas into six governance zones by cross-mapping spatial significance with temporal patterns, identified 779 association rules with an average confidence of 82.9%, and generated event-type association heatmaps based on correlation matrices to support business analysis.
4. Evaluated clustering quality using the Silhouette Coefficient and Calinski–Harabasz Index, and validated identified associations through Pearson correlation analysis to improve the interpretability and analytical reliability of the results.
5. Developed an interactive visualization dashboard and deployed the analytical pipeline as a FastAPI microservice with Docker support, enabling reproducible analysis and integration with the existing governance information system.

### Guangzhou Finance Holdings Group Co., Ltd | 07/2025–08/2025

*Position: Property Management Intern · Mentor: Dianhan Wei · Guangzhou, China*

**Property Management Documentation and Financial Data Analysis**

1. Systematically organized and summarized approved proposals by time period and category using Excel, improving the accessibility and traceability of documentation.
2. Analyzed meeting minutes and proposal documents to extract and reconcile key financial data, including budget allocations, audited revenues, and post-audit profit figures, ensuring data accuracy and consistency.
3. Identified and documented core approval requests and financial implications raised in proposals, providing clear, quantitative support for senior management decision-making.

## Research Experience

### Method-Level Reproduction of a CT Radiomics Survival Model (Aerts et al., 2014) | 10/2026–Present

*Research Internship Project, [Company / Lab] · Mentor: [Name]*

**Innovation Points:** Tested whether an open-source PyRadiomics pipeline can reproduce the CT-radiomics → Cox survival workflow of Aerts et al. (Nature Communications, 2014) on the Lung1 cohort (422 patients; 399 analyzed), and quantified the signature's prognostic signal relative to routine clinical variables.

**Workloads:**

1. Built a reproducible Docker + Conda environment (PyRadiomics 3.0.1 compiled from source, NumPy 1.26.4, build-time import checks); ingested the full 422-patient TCIA DICOM CT/RTSTRUCT dataset and reconstructed GTV-1 masks from RTSTRUCT contours via even-odd rasterization with ROI-name normalization.
2. Implemented an idempotent, chunked multiprocessing pipeline (per-case cache keyed by parameter and script SHA-256, pool recycling) that extracts 537 features per case under paper-aligned settings (25 HU bin width, no resampling, Coif1 wavelet) at ~26 s/case (cold cache); diagnosed repeated OOM failures and isolated a 297-slice scan exceeding the 8 GB container limit.
3. Built a leakage-free evaluation pipeline on a pre-specified 399-patient / 352-event analysis set with 5-fold × 10-repeat stratified CV (seed 42, 50 held-out folds, ~49 min); variance/correlation filtering, univariate Cox screening and LASSO-Cox were all fitted inside each training fold, and Harrell's C-index, train−test optimism gap and per-feature selection frequency were reported.

**Results:** Extracted 537 features for all 422 patients with zero non-finite values. Compactness 2 and GLRLM GLN matched the paper's Lung1 medians (×1.01, ×0.97); Energy matched at ×1.03 once expressed on the paper's HU+1024 convention (raw-HU ×0.03 is a sensitivity), while wavelet-HLH GLN remained ×1.88, reflecting implementation differences. On the fixed 399-patient set, the reconstructed 4-feature signature (weights self-fitted) reached a 5×10 CV C-index of 0.581 ± 0.038, versus 0.530 ± 0.026 for clinical variables alone, 0.583 ± 0.035 for in-fold LASSO-Cox, and 0.581 ± 0.034 for the combined model — no gain over imaging alone. All four features showed the paper-consistent univariate direction (HR/SD: Energy 1.13, GLN 1.20, Compactness 2 0.90 (borderline), wavelet GLN 1.21), a qualitative check only. LASSO kept 11.3 features per fold (range 2–42; 99 features selected at least once, only one above 80%) and selected only one of the 4 signature features (8% of folds) yet matched its performance, so the work is scoped as a method-level reproduction — the paper reported no Lung1 training C-index and did not publish the Cox weights.

### Volatility-Enhanced Time Series Modeling for Stock Index Return Prediction | 07/2026–09/2026

*Undergraduate Research Project, City University of Hong Kong · Advisor: Prof. Jinfeng Xu*

**Innovation Points:** Investigated whether incorporating lagged market volatility into autoregressive time-series models improves the prediction of weekly stock index returns across the S&P 500, Dow Jones, and NASDAQ.

**Workloads:**

1. Collected and processed daily market data from 2015 to 2026 using Python, constructing weekly log returns and lagged volatility measures for the S&P 500, Dow Jones, and NASDAQ and implementing a chronological 80/20 train-test split.
2. Developed and compared AR(1), volatility-augmented ARX, and higher-order AR(p) models, using AIC/BIC for model selection and Ljung–Box, residual ACF, and Jarque–Bera tests for model diagnostics.
3. Evaluated out-of-sample forecasting performance using RMSE, MAE, and directional accuracy, and implemented expanding-window re-estimation as a robustness check across all three market indices.

**Results:** Incorporating lagged volatility reduced out-of-sample RMSE by 0.94%, 0.43%, and 0.61% for the S&P 500, Dow Jones, and NASDAQ, respectively, with improvements persisting under expanding-window evaluation. However, directional accuracy did not consistently improve, indicating that lagged volatility provides only limited incremental predictive value for weekly stock returns.

<!-- 新增条目按此结构追加：标题 | 时间 / 项目类型与机构 · 导师 / Innovation Points / Workloads 1–3 / Results -->

## Academic Projects

### Medical Text Matching for Patient Questions | 06/2026

*Position: Team Member · Advisor: Prof. Maria Isabel Bueno Cachadina · Course Project of Applied Linear Algebra*

1. Developed a medical text-matching pipeline to retrieve relevant PubMed articles from short patient symptom descriptions across migraine, asthma, and respiratory infection topics.
2. Implemented TF-IDF, SVD, and cosine similarity for document retrieval, reducing 1,073 text features to 5 latent dimensions while retaining approximately 41.9% of the variance.
3. Evaluated retrieval performance using Top-1 and Top-3 Accuracy and benchmarked the approach against a keyword-matching baseline.

### Graph-Based Topic Classification via Label Propagation | 05/2026

*Position: Team Member · Advisor: Prof. Maria Isabel Bueno Cachadina · Course Project of Applied Linear Algebra*

1. Built a graph-based semi-supervised text classification model on the 20 Newsgroups dataset, representing documents with TF-IDF features and constructing a weighted k-nearest-neighbor graph using cosine similarity.
2. Implemented graph Laplacian label propagation by solving the regularized sparse linear system `L_uu f_u = −L_ul f_l`, achieving 96.22% classification accuracy on 1,800 unlabeled documents using only 100 labeled samples.
3. Compared sparse LU and Cholesky factorization for the 1,800-dimensional Laplacian system, achieving a 1.36× runtime speedup with Cholesky while maintaining relative residuals on the order of 10⁻¹⁵.

### Facial Image & Sports Data Analysis with PCA/SVD | 06/2026

*Position: Team Member · Advisor: Prof. Maria Isabel Bueno Cachadina · Course Project of Applied Linear Algebra*

1. Applied SVD and PCA to 400 facial images with 10,304 pixel features, extracting eigenfaces and projecting high-dimensional image data into a lower-dimensional latent space.
2. Built and evaluated low-rank image reconstructions, retaining 90.1% of variance with 111 principal components while achieving a 3.47× compression ratio; analyzed reconstruction error using the Frobenius norm.
3. Extended the PCA pipeline to 705 NBA player-season observations across 26 statistical features, reducing the data to 2 principal components explaining 92.2% of total variance and interpreting major axes of player involvement and starter status.

## Skills & Awards

**Programming Languages:** Python, R, LaTeX, conda, -cuda-, dicom, docker, linux, agent(试用codex, cluade code, dsh)