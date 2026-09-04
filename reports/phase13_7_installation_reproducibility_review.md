# Phase 13.7 — Installation & Reproducibility Review

## Status
**PASS**

## Environment Verification
Documented the standard virtual environment setup logic (using standard Python `venv`) tailored explicitly for both Git Bash and PowerShell Windows environments. 

## Dependency Verification
Confirmed `requirements.txt` strictly against the source imports. Packages like `torch`, `torchvision`, `streamlit`, `grad-cam`, `opencv-python`, `Pillow`, `numpy`, `pandas`, `scikit-learn`, and `matplotlib` were correctly identified and justified by their specific utility within the application's preprocessing and modeling workflows.

## Git Exclusion Verification
Executed `git check-ignore` commands which confirmed the `.gitignore` policy excludes `models/best_finetuned_model.pth`, `auth/users.json`, and the `data/` directories. Also confirmed the existing repository flaw where `history/prediction_history.csv` is actively tracked instead of ignored.

## Model Setup Verification
Confirmed the requirement for `models/best_finetuned_model.pth` and explicitly documented that inference cannot execute without manual acquisition of this heavy binary artifact.

## Dataset Setup Verification
Confirmed the prerequisites surrounding the HAM10000 dataset, establishing that users must manually reconstruct the `data/raw/` path to execute splitting/training logic.

## Authentication Verification
Confirmed that local auth configuration naturally intercepts empty/missing `auth/users.json` states, meaning first-user setup works reliably upon fresh cloning.

## Offline Verification
Confirmed offline inference behavior. The system restricts its computational scope strictly to the local PyTorch environment, local CSVs, and local JSON IO, utilizing zero active internet endpoints during Streamlit operation.

## README Consistency
The current `README.md` (redesigned in Phase 13.2) accurately mirrors these installation and reproducibility constraints, correctly citing the GitHub size limits and `.gitignore` logic. No contradictions were found, therefore no modifications to `README.md` were necessary.

## Reproducibility Limitations
Documented that full "push-button" reproducibility from a GitHub clone is structurally impossible by design. Acquiring exact inference capabilities requires local assembly of the dataset and non-tracked model weights.

## Files Changed
- `reports/phase13_7_installation_and_reproducibility.md` (Created)
- `reports/phase13_7_installation_reproducibility_review.md` (Created)

## Validation
- `python -m py_compile app/app.py`: PASS (Code 0)
- `git diff --check`: PASS (Code 0)
- `git check-ignore` results:
  - `auth/users.json`: Ignored (.gitignore:50)
  - `models/best_finetuned_model.pth`: Ignored (.gitignore:22)
  - `data/raw` / `data/processed`: Ignored (.gitignore:44, .gitignore:48)
  - `history/prediction_history.csv`: **NOT IGNORED** (Active tracking flaw identified)

## Remaining Issues
The `history/prediction_history.csv` file remains incorrectly tracked in Git, preventing clean local privacy separation out-of-the-box.
