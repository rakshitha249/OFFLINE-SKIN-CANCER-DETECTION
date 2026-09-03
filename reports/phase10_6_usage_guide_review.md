# Phase 10.6 Usage Guide Review

## Application Behavior Reviewed
`app/app.py` was systematically reviewed to document actual UI features, thresholds, probability margins, image quality mechanics, and error states. No invented behaviors were included.

## Setup Instructions
Accurate bash commands for cloning, virtual environment creation, and dependency installation were integrated, matching the repository's structure.

## Model Checkpoint Instructions
Explicitly stated that the application requires `models/best_finetuned_model.pth`, which is intentionally excluded from Git. Confirmed that users must source or reproduce this file separately.

## Image Upload
Verified that `jpg`, `jpeg`, and `png` formats are strictly supported through the `st.file_uploader`.

## Model Output Explanation
Documented the output hierarchy: Model prediction (Malignant-Suspicious / Non-malignant), Estimated model probabilities, Decision threshold (0.50), and Threshold distance. Emphasized these are statistical metrics, not medical risks.

## Threshold Explanation
Transcribed the exact interpretation states from the code (`Near-threshold model output`, `Moderate distance from threshold`, `Model output is farther from the decision threshold`).

## Image Quality
Described the programmatic evaluations of Resolution, Brightness, and Sharpness. Clarified that these do not block inference but provide contextual warnings.

## Grad-CAM
Adopted the specific project language: "Grad-CAM describes regions that contributed more strongly to the model output. It is an explainability visualization and is not a medical diagnostic map."

## Prediction History
Verified the storage path `history/prediction_history.csv` and the CSV schema structure. Reiterated that this is a localized application log, not a medical record.

## Error Handling
Documented expected fail-states directly from `app.py`, including the missing-model hard stop, corrupted image exceptions, missing history UI state, and Grad-CAM generation failure. 

## Offline Operation
Reinforced the strictly offline, local execution nature of the app (local CPU/GPU, local inference, no cloud APIs).

## Troubleshooting
Generated a realistic troubleshooting table covering actual known issues (environment errors, missing checkpoints, unprocessable images).

## Safety Language
The usage guide rigorously segregates AI statistical output from medical terminology. Banned words (e.g., "safe", "dangerous", "diagnosis") were successfully avoided when describing functionality, adhering strictly to the safety audit constraints.

## README Changes
The existing "Running the Application" section was replaced with a more comprehensive "Application Usage" block linking to the detailed `reports/application_usage_guide.md`. 

## Verification
- Verified compilation `python -m py_compile app/app.py`
- Executed `git diff -- README.md` to ensure correct modifications.
- Checked `git status`

## Files Changed
- `reports/application_usage_guide.md` (Created)
- `reports/phase10_6_usage_guide_review.md` (Created)
- `README.md` (Modified)

*Note: No model architectures, inference behaviors, datasets, or evaluation artifacts were changed. This was entirely a documentation phase.*
