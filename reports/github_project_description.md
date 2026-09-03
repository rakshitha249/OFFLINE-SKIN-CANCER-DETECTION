# GitHub Project Description

## Short GitHub Description
An offline PyTorch and Streamlit educational prototype for binary skin lesion classification, featuring EfficientNet-B0 transfer learning and Grad-CAM explainability.

## Medium Description
This project is an AI research and educational prototype that implements an end-to-end machine learning pipeline for analyzing the HAM10000 skin lesion dataset. It combines a carefully fine-tuned EfficientNet-B0 PyTorch model with a localized Streamlit application to provide offline inference, extensive test-set evaluation, and Grad-CAM explainability without requiring cloud dependencies.

## Project Highlights
- **Strict Data Splitting:** Utilizes `GroupShuffleSplit` on physical lesion IDs (70/15/15) to prevent data leakage across the 10,015-image dataset.
- **Transfer Learning:** Custom fine-tuning of an EfficientNet-B0 backbone using PyTorch and `BCEWithLogitsLoss`.
- **Quantitative Evaluation:** Achieved 85.37% ROC-AUC and 90.88% recall on a rigorous 1,494-image held-out test set.
- **Offline Inference:** Fully localized Streamlit web application requiring no external APIs or cloud computation.
- **Explainability:** Integrated Grad-CAM visualization to highlight image regions contributing to the statistical model output.
- **Image Quality Analysis:** Programmatic heuristic checks for resolution, brightness, and sharpness.
- **Comprehensive Analysis:** Deep error and threshold analysis documenting systematic false positive patterns (e.g., NV and BKL classes).
- **Local History:** CSV-based localized logging of historical application outputs.

## Suggested GitHub Topics
machine-learning, deep-learning, computer-vision, pytorch, efficientnet, grad-cam, streamlit, image-classification, transfer-learning, python
