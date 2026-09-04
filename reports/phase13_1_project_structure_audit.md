# Phase 13.1 — Project Structure Audit

## 1. Overall Status
**PASS WITH WARNINGS**

## 2. Repository Structure
The project maintains a clean and logical structure:
```text
OFFLINE-SKIN-CANCER-DETECTION/
│
├── app/               # Streamlit application
├── src/               # Python source scripts
├── data/              # Dataset directory
│   ├── raw/
│   └── processed/
├── models/            # Saved PyTorch checkpoints
├── history/           # Local application logs
├── auth/              # Local authentication data
├── reports/           # Generated documentation and metrics
├── .venv/             # Virtual environment
├── .gitignore         # Version control exclusion rules
├── requirements.txt   # Python dependencies
└── README.md          # Project overview
```

## 3. Component Responsibilities
- **`app/`**: Contains `app.py`, the offline Streamlit web application providing UI, authentication, and local inference capabilities.
- **`src/`**: Houses the entire machine learning pipeline scripts (`create_splits.py`, `train.py`, `finetune.py`, `evaluate.py`, `error_analysis.py`).
- **`data/`**: Stores the raw HAM10000 images and metadata (`raw/`), and the locally generated train/val/test CSV splits (`processed/`).
- **`models/`**: Secure local storage for PyTorch model weights (e.g., `best_finetuned_model.pth`).
- **`history/`**: Stores `prediction_history.csv`, which tracks local usage and model outputs across sessions.
- **`auth/`**: Stores `users.json`, managing local hashed credentials.
- **`reports/`**: The central repository for all generated markdown documentation, evaluation CSVs, and visualization plots.
- **`requirements.txt`**: Standardized package management ensuring reproducible environments.
- **`.gitignore`**: Enforces Git hygiene by blocking heavy models, large datasets, caches, and sensitive credentials from being committed.

## 4. ML Pipeline
The actual end-to-end machine learning pipeline executes as follows:
Dataset ingestion (HAM10000) → Preprocessing and binary label mapping (`create_binary_dataset.py`) → GroupShuffleSplit to prevent data leakage (`create_splits.py`) → Initial training with augmentations (`train.py`) → Dynamic fine-tuning (`finetune.py`) → Saving the best checkpoint to `models/` → Held-out test evaluation (`evaluate.py`) → Extensive error analysis and artifact generation (`error_analysis.py`, `threshold_analysis.py`).

## 5. Application Pipeline
The Streamlit application enforces the following workflow:
Local User Authentication (gated access via PBKDF2 hashing) → Image Upload (JPG/PNG) → RGB Preprocessing → Local EfficientNet-B0 inference → Probability calculation via Sigmoid → Threshold-based classification (0.50 boundary) → Programmatic image quality analysis (resolution/brightness/sharpness) → Grad-CAM overlay generation → Transparent reporting of outputs → Logging to local `prediction_history.csv`.

## 6. Model Configuration
- **Architecture:** EfficientNet-B0 feature extractor.
- **Classification Head:** Linear layer tailored for binary classification (Non-malignant vs Malignant-Suspicious).
- **Input Size:** 224x224 RGB.
- **Preprocessing:** Standard ImageNet normalization (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).
- **Output Interpretation:** A single binary logit passed through a Sigmoid function to derive estimated model probability.
- **Decision Threshold:** Firmly set at 0.50.
- **Grad-CAM Implementation:** Targets the final convolutional layer of the EfficientNet-B0 backbone (`features[-1][0]`).

## 7. Evaluation Artifacts
Important verification artifacts are present and reflect the expected final metrics:
- **`models/best_finetuned_model.pth`**: The final trained weights.
- **`reports/final_metrics_summary.csv`**: Accurately reflects Accuracy (68.47%), Precision (39.53%), Recall (90.88%), Specificity (62.41%), F1 (55.10%), ROC-AUC (85.37%), with the exact confusion matrix (TN=734, FP=442, FN=29, TP=289).
- **`reports/error_analysis_report.md`**: Details the visual and probabilistic failure cases of the model.
- **`reports/consolidated_evaluation_report.md`**: Provides high-level statistical context.
- **`reports/threshold_analysis.csv`**: Demonstrates precision/recall trade-offs across probability thresholds.
- **`reports/reproducibility_review.md`**: Highlights environment and dataset constraints.

## 8. Git Hygiene
- `auth/users.json` is correctly ignored and tracked locally.
- `models/` and `data/` contents are correctly ignored to preserve repository size.
- **WARNING**: `history/prediction_history.csv` is being tracked by Git. It appears in the `git status` output as a modified file rather than an untracked/ignored file.
- **WARNING**: Several temporary script files (`update_app.py`, `update_table.py`) remain in the root directory as untracked files.

## 9. Security/Privacy Check
- Passwords stored in `auth/users.json` are securely hashed using PBKDF2-HMAC-SHA256 with a unique random salt. No plaintext credentials exist.
- No API keys, cloud tokens, or personal identifiers are exposed.
- User uploaded images are processed entirely in memory and are not permanently saved.

## 10. Offline Operation
The project robustly fulfills its offline requirements. 
- The EfficientNet-B0 model weights are loaded strictly from the local `models/` directory without triggering remote downloads.
- `streamlit run app/app.py` requires no network connection.
- Authentication validates directly against local JSON files.
- The Grad-CAM library computes heatmaps natively using PyTorch gradients.

## 11. Documentation Readiness
The current `README.md` is substantial, accurately detailing the technology stack, binary mapping, data splitting methodology, evaluation results, and architectural workflow. It contains the necessary safety disclaimers. 
**Needs Improvement:** While technically comprehensive, it lacks the polish required for an immediate professional portfolio drop. Installation instructions need consolidation, embedded visual links for screenshots are pending, and instructions for reproducibility on fresh clones must be clarified.

## 12. Issues Found
- **Critical:** None.
- **Important:** `history/prediction_history.csv` is actively tracked by Git and missing from `.gitignore`, which risks committing user session logs to version control.
- **Minor:** Temporary update scripts leftover from earlier phases clutter the project root.

## 13. Recommended Next Step
Phase 13.2 should focus on improving the README/documentation based on this audit, securing `history/prediction_history.csv` via `.gitignore` updates, and cleaning up residual root scripts.
