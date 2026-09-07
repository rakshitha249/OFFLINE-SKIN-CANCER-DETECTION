# Phase 15.2 Public Demo Preparation

## 1. Public Demo Architecture
The public demo uses a completely separate entry point: `app/public_demo.py`. It inherits the core ML inference, Grad-CAM, and Image Quality logic directly from the offline version, but adapts the application shell (authentication, data persistence, and model loading) specifically for ephemeral cloud environments like Streamlit Community Cloud or Hugging Face Spaces.

## 2. Difference Between Local/Offline and Hosted Versions
- **Local/Offline (`app/app.py`):** Requires local file access for `users.json`, appends all predictions to a persistent local `prediction_history.csv`, and assumes the `.pth` model exists locally.
- **Hosted (`app/public_demo.py`):** Requires no login. Uses strictly ephemeral session history. Dynamically retrieves the `.pth` model from an external URL if not found locally.

## 3. Authentication Approach
Local authentication (`users.json`) has been completely removed from `app/public_demo.py`. The hosted version opens directly into the application, allowing immediate access for portfolio reviewers without requiring credentials. The local `app/app.py` retains its strict PBKDF2 authentication.

## 4. Prediction-History Approach
The `save_prediction_history` and `load_prediction_history` functions were rewritten in `public_demo.py` to use `st.session_state["history"]` instead of writing to `history/prediction_history.csv`. This ensures:
- History is isolated to the specific visitor's session.
- No visitor data is permanently stored on the host server.
- The history automatically resets when the visitor closes the browser tab.

## 5. Model Retrieval Approach
Instead of hardcoding a model path or failing when the git-excluded `.pth` is missing, `app/public_demo.py` uses the standard library `urllib.request` to dynamically retrieve the model. 
- It checks if `models/best_finetuned_model.pth` exists.
- If not, it attempts to download it from the URL specified in the `MODEL_URL` environment variable.
- If `MODEL_URL` is unconfigured, it fails gracefully with a clear warning string.
*(No actual URL was provided or hardcoded yet).*

## 6. Privacy Approach
Because authentication and global prediction history were stripped, no visitor data is persisted to the server file system. Uploaded images remain in Streamlit's ephemeral memory, and history vanishes on session end. The local `history/` and `auth/` directories are completely ignored.

## 7. Grad-CAM Handling
The Grad-CAM logic remains mathematically identical. The medical safety disclaimer has been preserved verbatim to clarify it is an explainability tool, not a diagnostic map.

## 8. Image-Quality Handling
The image-quality calculations (Resolution, Brightness, Sharpness) remain mathematically identical to the offline application, preserving the exact thresholds and warning triggers.

## 9. Safety Language
The safety disclaimer remains exactly the same as the offline version ("This project is an AI research and educational prototype..."). No diagnostic language (e.g., "cancer detected", "clinical confidence") was introduced.

## 10. Streamlit Entry Point
The public deployment can be launched via:
`python -m streamlit run app/public_demo.py`

## 11. Dependencies
The `requirements.txt` file was audited. Because the model retrieval was implemented using Python's built-in `urllib.request`, no new external dependencies (like `requests`) needed to be added. The existing `requirements.txt` is fully sufficient.

## 12. Deployment Prerequisites
To deploy this successfully, the hosting environment must provide:
1. `MODEL_URL` environment variable pointing to the raw `.pth` file.
2. The current `requirements.txt`.
3. The GitHub repository code.

## 13. Remaining Steps Before Deployment
1. Upload `best_finetuned_model.pth` to a deployment-safe host (e.g., Hugging Face Models, AWS S3, or GitHub Releases).
2. Configure the `MODEL_URL` secret/environment variable on the chosen hosting platform (e.g., Streamlit Community Cloud settings).

## 14. Risks/Warnings
- **Memory Consumption:** The model inference and Grad-CAM computations consume RAM. Free-tier hosts (1GB limit) may crash if multiple users evaluate images concurrently.
- **Model URL Stability:** If the external host providing the `.pth` file goes down or changes its direct-download link structure, the deployment will fail to boot on new containers.
