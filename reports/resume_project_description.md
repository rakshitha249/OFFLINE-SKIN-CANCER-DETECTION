# Resume Project Description

## Project Title
Offline Skin Lesion Analyzer: EfficientNet-B0 Binary Classification Prototype

## One-Line Description
Developed an offline AI educational prototype that classifies skin lesion images using a fine-tuned EfficientNet-B0 model, featuring local Streamlit inference and Grad-CAM explainability.

## Resume Version — 3 Bullet Points
- Engineered an end-to-end binary image classification pipeline in PyTorch utilizing EfficientNet-B0 and the HAM10000 dataset, employing `GroupShuffleSplit` on physical lesion IDs to guarantee strict test-set isolation across 10,015 images.
- Designed a custom fine-tuning workflow with dynamic positive-class weighting and validation ROC-AUC checkpointing, achieving 85.37% ROC-AUC and 90.88% recall on a rigorous 1,494-sample held-out test split.
- Developed an offline-first Streamlit web application integrating PyTorch local inference, heuristic image-quality assessments, and Grad-CAM heatmap explainability to visualize statistical model behavior without cloud dependencies.

## Resume Version — 4 Bullet Points
- Engineered an end-to-end binary image classification pipeline in PyTorch utilizing EfficientNet-B0 and the HAM10000 dataset, employing `GroupShuffleSplit` on physical lesion IDs to guarantee strict test-set isolation.
- Implemented a robust training workflow utilizing `BCEWithLogitsLoss`, AdamW optimization, dynamic class-weighting, and strategic layer unfreezing, resulting in 85.37% ROC-AUC on the held-out test set.
- Executed comprehensive evaluation and error analysis across probability thresholds, demonstrating a 90.88% recall boundary while systematically documenting false positive concentrations within specific original diagnostic categories.
- Developed an offline Streamlit web application providing local inference, Grad-CAM explainability visualizations, and heuristic image-quality assessments, entirely containerized within a localized Python environment.

## ATS Keywords
Python, PyTorch, EfficientNet, Computer Vision, Deep Learning, Binary Classification, Transfer Learning, Grad-CAM, Streamlit, Scikit-learn, Model Evaluation, ROC-AUC, Image Classification, Data Augmentation, Pandas, NumPy.

## Skills Demonstrated
- **Machine Learning:** Transfer Learning, Binary Classification, Loss Weighting, Hyperparameter Tuning.
- **Computer Vision:** Image Preprocessing, Data Augmentation, Convolutional Neural Networks (EfficientNet-B0).
- **Python/Software:** PyTorch, Pandas, NumPy, Virtual Environments, Modular Scripting.
- **Evaluation:** Strict Data Splitting (`GroupShuffleSplit`), ROC-AUC analysis, Threshold Analysis, Confusion Matrix, Error Pattern Documentation.
- **Application Development:** Streamlit, Local Offline Inference, UI/UX Design, Explainability (Grad-CAM), Logging (CSV).
