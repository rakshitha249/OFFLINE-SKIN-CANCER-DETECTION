# Phase 13.6 — Screenshot & Demo Plan

## 1. Purpose

The purpose of capturing screenshots is to visually demonstrate the actual working Streamlit user interface of the Offline Skin Lesion Analyzer. High-quality screenshots are essential for GitHub README presentations, academic portfolios, and technical interviews, providing immediate context for the application's capabilities, layout, and localized offline processing.

## 2. Recommended Screenshots

Currently, no application screenshots exist within the repository. The following table outlines the required screenshots that must be captured manually to guarantee authenticity.

| Screenshot | Purpose | Required |
|---|---|---|
| **Login Screen** | Demonstrates the secure local authentication portal and first-user setup mechanism. | Yes |
| **Main Dashboard** | Shows the default application state, sidebar metadata, safety disclaimers, and the file upload interface. | Yes |
| **Model Output** | Displays the model prediction, estimated model probabilities, continuous distribution bar, and threshold distance context. | Yes |
| **Image Quality** | Highlights the heuristic evaluation of resolution, brightness, and sharpness. | Yes |
| **Grad-CAM** | Visualizes the explainability overlay highlighting regions contributing to the model prediction. | Yes |
| **Prediction History** | Showcases the local CSV-backed logging table and dynamic session summary metrics. | Yes |
| **Dark Mode UI** | Demonstrates the application's native responsiveness to OS dark-mode themes. | Yes |

## 3. Capture Guidelines

To maintain a professional, academic standard, all manual captures must adhere to the following guidelines:
- **Authenticity**: Use actual running application screenshots. Do not fabricate or composite UI elements.
- **Privacy**: Avoid capturing personal identifiers, developer system file paths, browser bookmarks, or sensitive desktop clutter.
- **Security**: Absolutely avoid showing plaintext passwords, and ensure the contents of `auth/users.json` are never exposed in terminal backgrounds.
- **Content**: Use a representative skin-lesion image from the test dataset to generate realistic Model Output, Image Quality, and Grad-CAM results.
- **Framing**: Capture the complete, relevant section of the UI. Use consistent dimensions (e.g., locking the browser window to 1280x800) for uniform presentation.

## 4. Recommended README Order

Once captured and stored (e.g., in `docs/screenshots/`), the visual flow in the README should logically mirror the user journey:
1. **Login**
2. **Main Dashboard / Upload**
3. **Model Output**
4. **Image Quality**
5. **Grad-CAM**
6. **Prediction History**
