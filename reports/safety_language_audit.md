# Phase 9.2 Safety and Medical-Language Audit

## 1. Changes Made
- Modified `app/app.py` to systematically address critical safety, wording, and error-handling concerns highlighted during the Phase 9.1 audit.
- No model, dataset, evaluation, or history mechanics were altered.

## 2. Prediction Terminology
- Replaced "Prediction" with "Model prediction".
- Removed hardcoded red/green color assignments for the prediction text that could imply definitive Danger/Safe medical diagnoses. Replaced with neutral bold text layout styling.

## 3. Probability Terminology
- Replaced "Prediction probability" with "Estimated model probability".
- Preserved the explicit disclaimer underneath the probability bar clarifying that the value is statistical, not medical.

## 4. Uncertainty Terminology
- Replaced "Uncertainty Assessment" section header with "Model Output Strength".
- Replaced clinical-sounding terms like "Higher model confidence" and "Low confidence" with statistically grounded wording such as "Farther from the decision threshold" and "Near-threshold model output".
- Emphasized that the logic purely reflects the distance from the threshold (0.50).

## 5. Visual Presentation
- Removed the red and green inline CSS tags for displaying "Malignant-Suspicious" and "Non-malignant".
- Relies instead on neutral formatting (`font-size: 20px; font-weight: bold;`) consistent with a research prototype.

## 6. Safety Disclaimer
- Implemented the user-requested, universally clear safety disclaimer at the top of the application sidebar/main page: *"This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions."*
- A similar strict warning is repeated directly below the inference results.

## 7. Missing Model Handling
- The critical `FileNotFoundError` bug has been fixed.
- `load_model()` now explicitly verifies `os.path.exists` before attempting to load the `.pth` file using `torch.load`.
- If the model is missing, it returns `None`. The main thread detects this, logs a graceful `st.error()` explaining exactly what file is required, and stops execution natively using `st.stop()`. 

## 8. Functionality Verification
- **Syntax Check:** Python `py_compile` confirmed valid syntax.
- **Missing-model scenario:** The logic handles `None` returned gracefully by halting execution, avoiding the crash.
- **Normal execution:** Preserved correctly since the checkpoint exists in the `models/` folder.
- **Core Functionality:** Unchanged. Grad-CAM, threshold limits (0.50), prediction calculations, image quality logic, and CSV writing histories are structurally identical and completely preserved.

## 9. Remaining Medical/Safety Language
- A semantic grep search was run for `diagnosis`, `confirmed`, `safe`, `healthy`, `cancer detected`, and `medical confidence`.
- **0 results** found corresponding to clinical claims.
- The remaining occurrences of the word "diagnosis" are exclusively found in the strict safety disclaimers explicitly explaining that the system does *not* provide a diagnosis.

## 10. Final Assessment
**PASS**
The application now safely frames all predictions as purely statistical model outputs. The UI correctly handles missing resources without fatal unhandled crashes, and the clinical implications of the interface have been effectively neutralized.
