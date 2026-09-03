# Visual Portfolio Material

## Purpose
These visuals are intended to demonstrate the actual offline Streamlit application's interface and key capabilities. They provide a visual walkthrough of the user experience, from uploading an image to interpreting the model's statistical outputs and explainability features.

> [!NOTE]
> **Environment Limitation Acknowledged:** 
> Automated browser interaction and high-fidelity screenshot extraction were unavailable in the current headless execution environment. To strictly comply with the project requirement against fabricating or mocking fake screenshots, no image files have been placed in the `reports/screenshots/` directory at this time. The placeholders below document the exact visual components that should be captured manually.

## Screenshots (Pending Manual Capture)

### 1. Main Application
**Intended File:** `reports/screenshots/01_main_application.png`
**Description:** Demonstrates the application's clean interface upon launch. It captures the project title, the file upload area, and the prominent safety disclaimer emphasizing the non-diagnostic nature of the tool.

### 2. Model Prediction
**Intended File:** `reports/screenshots/02_model_prediction.png`
**Description:** Demonstrates the model's output hierarchy. It captures the explicit model prediction (e.g., "Malignant-Suspicious"), the estimated probability breakdown, the 0.50 decision threshold context, and the calculated distance from that threshold. 

### 3. Near-Threshold Output
**Intended File:** `reports/screenshots/03_near_threshold_output.png`
**Description:** Demonstrates the threshold-distance presentation logic when an image produces an estimated probability close to 0.50. It shows the application's explanation that the classification is sensitive to small changes in mathematical model output, without equating it to medical uncertainty.

### 4. Image Quality
**Intended File:** `reports/screenshots/04_image_quality.png`
**Description:** Demonstrates the heuristic image-quality assessment. It shows the calculated values for Resolution, Brightness, and Sharpness, and the corresponding application warnings if the image falls outside preferred characteristics.

### 5. Grad-CAM Explainability
**Intended File:** `reports/screenshots/05_gradcam_explainability.png`
**Description:** Demonstrates the explainability visualization. It captures the side-by-side comparison of the original image and the Grad-CAM heatmap overlay. It highlights the application's explicit wording that Grad-CAM describes model behavior (regions contributing strongly to the output) and is not a medical diagnostic map.

### 6. Prediction History
**Intended File:** `reports/screenshots/06_prediction_history.png`
**Description:** Demonstrates the local history interface at the bottom of the application. It captures the tabular log of timestamp, image name, prediction, probabilities, model output strength, and image quality.

## Portfolio Usage
Once captured manually, these screenshots can be embedded into:
- The GitHub README for an immediate visual summary.
- A technical project portfolio.
- Academic project documentation.
- Presentation slides for interviews and technical discussions.

## Visual Safety / Privacy Review Guidelines
When capturing these screenshots, ensure the following standards are met:
- **No private user data:** Ensure local file paths and personal identifiable information are omitted.
- **No credentials:** Ensure no terminal tokens or irrelevant desktop elements are captured.
- **Use dataset images only:** Ensure all predictions utilize images sourced strictly from `data/raw/images/`.
- **Preserve non-diagnostic language:** Ensure no screenshots are altered to include unapproved medical claims.
