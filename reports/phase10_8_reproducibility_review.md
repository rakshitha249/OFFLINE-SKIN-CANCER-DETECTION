# Phase 10.8 Reproducibility & Limitations Review

## Scope
This phase documented the strict reproducible capabilities of the repository and codified the limitations surrounding dataset exclusions, training environments, performance constraints, and threshold parameters.

## Fresh Clone Review
Confirmed via `.gitignore` that `data/raw/`, `data/processed/`, `models/`, and `.venv/` are intentionally omitted. Documented explicitly that a fresh clone cannot immediately perform inference.

## Dataset Review
Confirmed the public HAM10000 baseline (10,015 images), its 7 diagnostic categories, the binary mapping mechanism, and the rigorous 70/15/15 `GroupShuffleSplit` across `lesion_id` resulting in exactly 1494 test images.

## Training Review
Documented the initial training structure (`AdamW` lr=0.0001, `BCEWithLogitsLoss`) and fine-tuning mechanism (lr=0.00001). Acknowledged that lack of explicit environment seeding may cause minor reproduction variances.

## Evaluation Review
Restated the authoritative metrics evaluated from the held-out test set (ROC-AUC 85.37%, Recall 90.88%, etc.) and correctly positioned them as statistical performance rather than clinical capability. 

## Application Review
Highlighted the strict necessity of the `models/best_finetuned_model.pth` file for Streamlit execution.

## Offline Operation Review
Successfully defined "offline" to explicitly refer to localized inference (models, image processing, Grad-CAM, CSV history) while clarifying that installation/cloning necessitates a network connection.

## Limitations Review
Detailed the profound limitations stemming from binary groupings, dataset biases, non-clinical threshold applications (fixed 0.50), and the missing inclusion of datasets/models in Git tracking.

## Safety Review
The `reports/reproducibility_and_limitations.md` file and `README.md` updates stringently adhere to safety language restrictions. They successfully frame the output as "estimated model probability" and avoid referring to "diagnoses" or "medically safe" predictions. The project disclaimer is preserved exactly as mandated.

## Factual Consistency Review
- Pinned packages listed strictly originate from `requirements.txt`.
- Data counts (1494 test images, 70/15/15 splits, 442 FP, 29 FN, 10015 total, 97.3% NV/BKL) precisely match the verified reports and codebase configuration.
- No details were invented regarding missing download links or unrecorded environments.

## Technical Validation
- Executed `python -m py_compile app/app.py`
- Executed `git diff -- README.md` 
- Checked `git status`
- **Confirmation:** No underlying logic (app.py, dataset, training, evaluation, UI) was altered.

## Remaining Gaps
- Model weights (`best_finetuned_model.pth`) cannot be reproduced from the repository alone without manually downloading HAM10000.
- Raw and processed datasets are intentionally excluded.

## Conclusion
Phase 10.8 Reproducibility & Limitations Complete.
