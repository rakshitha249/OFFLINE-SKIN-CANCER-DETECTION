# Phase 15.8 Final Deployment Audit

## 1. Deployment Status
The Streamlit public demo was successfully redeployed from a fresh environment and manually verified by the user to be fully functional.

## 2. Deployment Configuration
- **GitHub Repository:** `rakshitha249/OFFLINE-SKIN-CANCER-DETECTION`
- **Branch:** `main`
- **Entrypoint:** `app/public_demo.py`
- **Python Version:** `3.12.14`
- **Streamlit Version:** `1.62.0`
- **Hosted Inference Architecture:** PyTorch CPU inference on Streamlit Community Cloud
- **Model Source:** Externally hosted `.pth` checkpoint securely downloaded to memory/disk on startup
- **GitHub Release Tag:** `v1.0-model`

## 3. Dependency Resolution
The original deployment failure (`ImportError: libGL.so.1`) was definitively traced to an environment cache retention issue on Streamlit Cloud:
- The old Streamlit container environment retained the GUI-enabled `opencv-python` package.
- The correct configuration strictly requires `opencv-python-headless==5.0.0.93`.
- `grad-cam==1.5.7` also explicitly requires `opencv-python-headless`.
- Deleting the Streamlit Cloud app and provisioning a fresh deployment installed only the headless variant.
- The `libGL.so.1` error no longer occurs.

## 4. Manual Live Tests

| Test | Result | Verification method |
|---|---|---|
| Test 1 — Application startup | PASS | Manual user verification |
| Test 2 — Image upload | PASS | Manual user verification |
| Test 3 — Model inference | PASS | Manual user verification |
| Test 4 — Model Output UI | PASS | Manual user verification |
| Test 5 — Image Quality | PASS | Manual user verification |
| Test 6 — Grad-CAM | PASS | Manual user verification |
| Test 7 — Prediction History | PASS | Manual user verification |
| Test 8 — Safety wording | PASS | Manual user verification |

## 5. Application Functionality
The public demo successfully executes the end-to-end pipeline:
- Image upload (JPG/PNG).
- Real-time CPU inference.
- Model Output display (prediction and estimated probability).
- Probability distribution visualization.
- Threshold context analysis and threshold distance.
- Image quality heuristic checks (resolution, brightness, sharpness).
- Grad-CAM explainability overlay generation.
- Session-isolated prediction history logging.

## 6. Safety / Medical-Language Review
The public demo maintains strict neutral terminology (e.g., "Malignant-Suspicious", "Estimated model probability", "Decision threshold"). It successfully displays the mandated safety disclaimer:
> "This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions."

## 7. Privacy / Repository Exposure
A security exposure check confirms the following sensitive items remain correctly ignored by Git and untracked:
- `auth/users.json`
- `history/prediction_history.csv`
- `models/`
- `data/raw/`
- `data/processed/`
- `.venv/`

No passwords, Streamlit secrets, API keys, or user-uploaded images are tracked in the repository.

## 8. Model Release
To preserve repository size limits and Git history cleanly, the ~25.4MB PyTorch model checkpoint is successfully distributed via the `v1.0-model` GitHub Release. It is not tracked in normal Git history. The model release description maintains the proper research/educational positioning.

## 9. Local vs Public Demo

**Local application:**
- Entrypoint: `app/app.py`
- Requires robust local authentication.
- Maintains a persistent local CSV prediction history.
- Relies on a locally present `models/best_finetuned_model.pth`.
- Executes entirely offline.

**Public demo:**
- Entrypoint: `app/public_demo.py`
- Features no login or authentication barrier.
- Stores prediction history only temporarily for the active browser session.
- Executes hosted inference via Streamlit Cloud.
- Dynamically retrieves the model from the GitHub Release via the `MODEL_URL` environment variable.

## 10. Known Limitations
- This is a research/educational prototype and is **not** a medical diagnostic device.
- Model performance is based strictly on the project's held-out test dataset; there is no clinical validation.
- The hosted public demo depends entirely on Streamlit Cloud availability and GitHub Release availability.
- CPU-based inference on the shared Streamlit tier may exhibit variable latency.
- The public demo does not provide persistent per-user history across sessions.

## 11. Final Status

| Audit Category | Status |
|---|---|
| Deployment Configuration | PASS |
| Dependency Stability | PASS |
| Public Demo UI | PASS |
| ML Pipeline Execution | PASS |
| Safety Wording & Privacy | PASS |
| Git History Integrity | PASS |
