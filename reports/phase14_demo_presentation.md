# Demo Presentation Plan

*A guide for delivering a professional 5–7 minute technical project demonstration.*

## 1. Introduction (0:30)
- **What to show:** Title slide or the login screen of the application.
- **Technical point:** Introduce the Offline Skin Lesion Analyzer as a privacy-first, offline computer vision prototype built with PyTorch and Streamlit.
- **Avoid:** Do not claim it is a medical device or a clinical tool.

## 2. Problem (0:20)
- **What to show:** Still on the login screen.
- **Technical point:** Cloud-based models require uploading sensitive image data. There is a need for robust, local-first inference systems.
- **Avoid:** Do not mention diagnosing patients.

## 3. Motivation (0:20)
- **What to show:** Login securely to the main dashboard.
- **Technical point:** Explain the desire to build a transparent AI system focusing on rigorous evaluation and explainable AI (XAI) rather than just a black-box probability output.

## 4. Architecture (0:30)
- **What to show:** Display a diagram of the architecture (or refer to it).
- **Technical point:** Mention EfficientNet-B0, PBKDF2 local authentication, and the local file-based prediction history.

## 5. Dataset (0:30)
- **What to show:** The upload interface.
- **Technical point:** Explain the use of the HAM10000 dataset, mapped to a binary problem. Emphasize the **lesion-grouped splitting strategy** that prevents data leakage by ensuring images of the same lesion do not cross train/test boundaries.

## 6. Model (0:30)
- **What to show:** Still on the upload interface.
- **Technical point:** Describe the fine-tuned EfficientNet-B0 architecture using ImageNet weights and transfer learning.

## 7. Training/Evaluation (0:45)
- **What to show:** Briefly show the ROC-AUC graph or the metrics summary (e.g., from the README).
- **Technical point:** Highlight the 85.37% ROC-AUC on the strictly held-out test set (1494 images). Mention that discrete metrics depend heavily on the chosen 0.50 threshold.

## 8. Application (0:30)
- **What to show:** Upload a sample image (e.g., a benign nevus or melanoma image from the dataset).
- **Technical point:** Demonstrate the fast, offline inference pipeline via Streamlit.

## 9. Model Output (0:30)
- **What to show:** The probability bar and classification result.
- **Technical point:** Explain that the output is a single logit passed through a Sigmoid activation. Emphasize how the app displays the distance from the 0.50 threshold to contextualize confidence.
- **Avoid:** Do not say the model "diagnosed" the image. Say "the model output an estimated probability of..."

## 10. Image Quality (0:20)
- **What to show:** The Image Quality metrics expander.
- **Technical point:** Explain the programmatic heuristics (resolution, brightness, sharpness) that provide context before inference.

## 11. Grad-CAM (0:45)
- **What to show:** Toggle the Grad-CAM visualization on the uploaded image.
- **Technical point:** Explain Gradient-weighted Class Activation Mapping. Show how it highlights the spatial regions the model used to make its classification, increasing interpretability.
- **Avoid:** Do not call it a "tumor detection map".

## 12. Prediction History (0:30)
- **What to show:** Navigate to the Prediction History tab.
- **Technical point:** Show how predictions, timestamps, and probabilities are logged locally to a CSV, enabling session review without a database or cloud backend.

## 13. Results (0:30)
- **What to show:** Return to the main dashboard.
- **Technical point:** Summarize the findings: high sensitivity (90.88%), but a substantial false-positive rate primarily driven by NV and BKL classes.

## 14. Limitations (0:30)
- **What to show:** The safety disclaimer on the UI.
- **Technical point:** Transparently discuss the class imbalance, threshold dependence, and lack of external dataset validation.
- **Avoid:** Do not hide the high false-positive rate. Acknowledging it shows engineering maturity.

## 15. Future work (0:20)
- **What to show:** Final view of the UI (perhaps toggling Dark mode).
- **Technical point:** Mention exploring multiclass approaches, advanced loss weighting, or comparing ResNet backbones.

## 16. Conclusion (0:15)
- **What to show:** Log out of the application.
- **Technical point:** Summarize the project as a successful offline, privacy-first computer vision pipeline emphasizing rigorous evaluation and explainability.
