# Phase 9.1 Offline Application Audit

## 1. Application Structure
- **`app/app.py`**: The sole application script that encapsulates the Streamlit UI, model loading, preprocessing, inference, visual explainability (Grad-CAM), and prediction history logging.

## 2. Model Loading
- **Checkpoint path:** `models/best_finetuned_model.pth`
- **Architecture:** `EfficientNet-B0`. It is explicitly loaded with `weights=None` to ensure it does not attempt to download pretrained ImageNet weights from the internet. The final classifier is replaced with a Dropout and Linear layer outputting 1 feature.
- **Device selection:** Automatically selects CUDA if available, falling back to CPU (`torch.device("cuda" if torch.cuda.is_available() else "cpu")`).
- **Loading behavior:** Encapsulated in a `load_model()` function decorated with `@st.cache_resource`, ensuring the model is loaded into memory only once per session.
- **Missing checkpoint behavior:** If the `.pth` file is missing, the application will encounter an uncaught `FileNotFoundError` during the initial script execution and crash with a traceback on the screen.

## 3. Image Processing
- **Accepted image types:** JPG, JPEG, and PNG (enforced by Streamlit's `file_uploader`).
- **Resizing:** Images are resized to `224 × 224`.
- **Normalization:** Standard ImageNet parameters used (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).
- **Preprocessing:** The uploaded PIL image is explicitly converted to RGB, transformed to a tensor, and normalized.
- **Handling of dimensions:** `transforms.Resize` forces the image to `224x224` regardless of the original aspect ratio. However, the image quality assessment function inspects the original dimensions before resizing.

## 4. Prediction Pipeline
- **Model inference:** Inference is executed inside a `with torch.enable_grad():` block (rather than `no_grad()`) because the gradients are strictly required to generate the Grad-CAM visualization.
- **Probability calculation:** The single raw output logit is converted to a probability using `torch.sigmoid(output_logit).item()`.
- **Threshold:** Hardcoded to `0.50`.
- **Prediction labels:** `1` triggers "Malignant-Suspicious", `0` triggers "Non-malignant".
- **Confidence interpretation:** A hardcoded logic tree assesses the distance of the probability from the threshold (`abs(probability - 0.5)`). Distances `< 0.10` are flagged as uncertain/low confidence, `< 0.25` as moderate confidence, and above as higher confidence.

## 5. Image Quality Assessment
- **Checks implemented:** 
  - **Resolution:** Checks if width/height is below 224 or 400.
  - **Brightness:** Converts to grayscale and calculates mean pixel intensity to classify as Dark, Normal, or Bright.
  - **Sharpness:** Calculates variance of adjacent pixel differences to estimate blurriness.
- **Status:** These checks are heuristic and basic. They are not medically validated. They flag potential issues (e.g., "Image appears blurry") but do not halt the inference pipeline.

## 6. Grad-CAM
- **Implementation:** Integrated using the `pytorch_grad_cam` library.
- **Target layer:** Specifically targets the final convolutional layer of the backbone: `model.features[-1][0]`.
- **Preprocessing:** The input tensor is explicitly set to `requires_grad_(True)`. A floating-point scaled array of the original image (`vis_img_np`) is used as the visual base.
- **Heatmap generation:** A custom class (`BinaryLogitTarget`) extracts the single logit for the Grad-CAM backward pass calculation.
- **Display:** The heatmap is overlaid onto the original image using `show_cam_on_image` and rendered via `st.image`.

## 7. Prediction History
- **Storage location:** Local CSV file at `history/prediction_history.csv`.
- **Fields stored:** Timestamp, Image Name, Prediction, Malignant Probability, Non-malignant Probability, Confidence, Image Quality.
- **Ordering:** Reversed before display so the newest records appear at the top.
- **Behavior when missing:** Handled gracefully. `load_prediction_history()` catches missing files/empty files and returns an empty list, displaying a clean "No prediction history available yet" message.

## 8. UI/UX
- **Page structure:** 
  - Sidebar: Model information and device status.
  - Main Body: Title, Medical Disclaimer, Image Uploader.
  - Results Section: Quality Assessment, Inference Metrics, Uncertainty Interpretation, Grad-CAM heatmap.
  - Footer: Prediction History table.
- **Result presentation:** Utilizes `st.metric` for probabilities, `st.progress` for visual proportion, and conditionally colored text (Red/Green) for the binary prediction.
- **Warnings:** Multiple disclaimers are present (top of page, under probability bar, inside uncertainty logic).
- **History display:** Renders via `st.dataframe` for clean tabular viewing.

## 9. Error Handling
- **Unsupported file type:** Prevented gracefully by Streamlit's file uploader configuration.
- **Corrupted image / Inference errors:** Caught by a broad `except Exception as e:` block spanning the analysis logic, which outputs a graceful `st.error` rather than crashing the app.
- **Missing model:** **Uncaught.** Crashes the application on startup.
- **Unexpected image dimensions:** Handled natively by the resizing transform; no crash occurs.
- **History file missing/empty:** Gracefully handled; directories and headers are created on the fly during saving.

## 10. Offline Requirement
- **Status:** Fully Offline. The application does not require network access during normal inference.
- **Local files used:** Requires `models/best_finetuned_model.pth`.
- **External URLs / Remote APIs:** None. Explicitly avoids downloading pretrained weights.

## 11. Safety Language Audit
- **User-visible terminology:** "Offline Skin Lesion Analyzer", "Malignant-Suspicious", "Non-malignant", "Higher model confidence".
- **Flagged wording:** 
  - **"Higher model confidence"**: Could be misinterpreted by a user as high medical certainty.
  - **Color Coding (Red/Green)**: Green implies "Safe" and Red implies "Danger". In a medical context with a known false-negative rate, telling a user they are "Green / Safe" is highly problematic.
  - The binary output labels, while caveated by disclaimers, are inherently clinical.

## 12. Strengths
- Fully offline design is perfectly implemented.
- Includes a practical uncertainty interpretation layer based on probability margins.
- Built-in heuristic image-quality checks (brightness/sharpness) add robustness.
- Explainability (Grad-CAM) is successfully implemented for a binary architecture.
- Clean, stateless history tracking without requiring complex database dependencies.

## 13. Issues and Recommendations
- **CRITICAL:** Missing model checkpoint causes a hard crash at startup. A `try/except` block around the model loading is required to show a graceful UI error advising the user to supply the `.pth` file.
- **IMPORTANT:** The Red/Green color coding for results may induce false confidence or panic; neutral colors (e.g., orange/blue or standard text) are significantly safer for prototypes.
- **IMPORTANT:** "Higher model confidence" should be softened to "Stronger statistical preference" to avoid implying diagnostic certainty.
- **NICE-TO-HAVE:** Add a "Clear History" or "Reset" button to allow users to flush the CSV easily.

## 14. Phase 9.1 Readiness
The application is highly structured, functionally complete, and strictly offline. It is fully ready to proceed to Phase 9.2 for safety-language improvements, UX tweaks, and final robustness testing. **(Note: This application remains an educational prototype and is not clinically ready).**
