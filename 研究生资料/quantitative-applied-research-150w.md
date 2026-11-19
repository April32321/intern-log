# Quantitative and Applied Research Experience

> Prompt: Please describe your quantitative and data analysis experience, as well as your applied research experience (150 words, required).

1. I reproduced Aerts et al.'s CT-radiomics → Cox workflow on the TCIA Lung1 cohort (422 patients; 399 analyzed), testing whether an open-source pipeline reproduces it and quantifying prognostic signal versus clinical variables.
2. Built a Docker + Conda environment (PyRadiomics 3.0.1, NumPy 1.26.4) and ingested the full CT/RTSTRUCT dataset, reconstructing GTV-1 masks via even-odd rasterization.
3. An idempotent multiprocessing pipeline extracted 537 features per case under paper-aligned settings (25 HU bins, Coif1 wavelet) at ~26 s/case, with zero non-finite values across 422 patients.
4. Evaluated models on a 399-patient / 352-event set with 5-fold × 10-repeat stratified cross-validation (seed 42), fitting filtering, screening, and LASSO-Cox inside training folds.
5. The self-fitted 4-feature signature reached C-index 0.581 ± 0.038 versus 0.530 ± 0.026 for clinical variables and 0.583 ± 0.035 for in-fold LASSO-Cox; LASSO kept 11.3 features per fold (2–42), with all four univariate directions matching the paper (Compactness2 borderline). A method-level reproduction, not independent validation.

<!-- Word count: 150 -->
