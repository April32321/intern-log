# Quantitative and Applied Research Experience

> Prompt: Please describe your quantitative and data analysis experience, as well as your applied research experience (150 words, required).

1. I reproduced Aerts et al.'s CT-radiomics → Cox workflow on the 422-patient TCIA Lung1 cohort, testing whether an open-source pipeline matches the original implementation and adds prognostic signal beyond clinical variables.
2. Built a Docker + Conda environment (PyRadiomics 3.0.1, NumPy 1.26.4) and ingested 26 GB of CT/RTSTRUCT data, reconstructing GTV-1 masks via even-odd rasterization.
3. An idempotent multiprocessing pipeline extracted 537 features per case under paper-aligned settings (25 HU bins, Coif1 wavelet) at ~25 s/case, with zero non-finite values across 422 patients.
4. Evaluated models on a fixed 399-patient / 352-event set with 5-fold × 10-repeat stratified cross-validation (seed 42), fitting filtering, screening, and LASSO-Cox inside training folds.
5. The 4-feature signature reached C-index 0.581 ± 0.038 versus 0.530 ± 0.026 for clinical variables and 0.583 ± 0.035 for in-fold LASSO-Cox; LASSO kept 11.3 features (range 2–42), with all four directions matching the paper, so this is a method-level reproduction, not independent validation.

<!-- Word count: 150 -->
