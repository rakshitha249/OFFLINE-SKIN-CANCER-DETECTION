# Technical Project Description

## Offline Skin Lesion Analyzer

### Problem Statement
Skin lesion analysis is a complex computer vision task that traditionally requires specialized medical expertise. The goal of this project was to develop a rigorous, fully offline machine learning pipeline capable of classifying dermatoscopic images as malignant-suspicious or non-malignant, prioritizing data privacy, rigorous evaluation, and explainable AI techniques.

### Motivation
Cloud-based AI models raise significant privacy concerns when handling sensitive image data. This project was motivated by the need to explore offline, local-first inference while implementing transparent evaluation metrics and explainability tools. This serves as a research and educational prototype to understand how convolutional neural networks interpret complex biological variations without making diagnostic claims.

### Dataset and Preprocessing
The project utilizes the HAM10000 dataset. To simplify the seven-class structure for this binary prototype, classes were mapped into a binary schema (Non-malignant vs. Malignant-Suspicious). 
Preprocessing involved standardizing image resolutions to 224x224 RGB and applying ImageNet normalization. Crucially, the dataset split utilized a lesion-grouped strategy based on `lesion_id` to ensure that multiple images of the exact same physical lesion did not straddle the training, validation, and testing boundaries, completely preventing data leakage.

### Model Architecture and Fine-Tuning
The core architecture is an EfficientNet-B0 convolutional neural network. 
A transfer learning approach was employed, starting with ImageNet pre-trained weights. The model underwent an initial training phase followed by a fine-tuning phase where specific layers were unfrozen. The model outputs a single logit passed through a Sigmoid activation to produce an estimated model probability between 0 and 1. Checkpoint selection was strictly based on validation performance across six epochs.

### Evaluation and Metrics
Evaluation was performed strictly on a held-out test set of 1494 images.
At the default 0.50 decision threshold, the model achieved:
- **Accuracy:** 68.47%
- **Precision:** 39.53%
- **Recall/Sensitivity:** 90.88%
- **Specificity:** 62.41%
- **F1 Score:** 55.10%

The confusion matrix (TN=734, FP=442, FN=29, TP=289) reveals high sensitivity but a substantial false-positive rate.
The model achieved an **ROC-AUC of 85.37%**, demonstrating strong overall discriminative capacity independent of any single threshold.

### Analysis (Threshold and Error)
A detailed threshold analysis demonstrated the heavy dependence of discrete metrics on the decision boundary.
Error analysis revealed that the vast majority of false positives stem from NV (melanocytic nevi) and BKL (benign keratosis) classes, while false negatives were predominantly MEL (melanoma) cases situated near the decision boundary (probabilities between 0.40 and 0.50).

### Explainability and Application
To provide visual context, **Grad-CAM** (Gradient-weighted Class Activation Mapping) is integrated into the inference pipeline, highlighting the spatial regions influencing the model's prediction. The system also includes basic programmatic **image-quality** heuristics (resolution, brightness, sharpness).

The entire pipeline is wrapped in a fully offline **Streamlit application** featuring:
- Local username/password authentication (PBKDF2-HMAC-SHA256).
- Local prediction history logging to CSV.
- Native Light/Dark/System theme support.
- Clear safety disclaimers emphasizing its nature as an educational prototype, not a medical device.

### Reproducibility and Limitations
The project enforces reproducibility through strict dependency pinning, deterministic lesion-grouped splits, and comprehensive evaluation artifacts.
Limitations include severe class imbalance, high false-positive rates on specific non-malignant subclasses, threshold dependence, and the absence of any external or clinical validation. The prototype fundamentally relies on statistical outputs and does not output medical diagnoses.
