# Reproducibility and Limitations

## 1. Reproducibility Overview
This project is an offline AI research and educational prototype. While the repository contains the complete pipeline (training scripts, application code, evaluation results), reproducing the application inference environment requires local assets that are intentionally excluded from the Git repository due to size and data constraints. 

## 2. Fresh Clone Requirements
A fresh Git clone provides the source code and reports but does **not** automatically contain:
- The HAM10000/raw image data
- The processed dataset split CSVs
- The trained model checkpoint
- The Python virtual environment (`.venv`)

As explicitly defined in `.gitignore`, these assets must be generated or provided locally. The exact environment is strictly defined in `requirements.txt` (e.g., `torch==2.13.0`, `torchvision==0.28.0`, `streamlit==1.62.0`).

## 3. Dataset Reproduction
The project requires the public HAM10000 dataset (10,015 images) with its original metadata CSV and image directories. The seven original classes are mapped into a binary schema:
- **Non-malignant:** NV, BKL, DF, VASC
- **Malignant-Suspicious:** MEL, BCC, AKIEC

The dataset is partitioned using `GroupShuffleSplit` grouping by `lesion_id` to strictly separate images of the same physical lesion across the Training (70%), Validation (15%), and Test (15%) splits, resulting in a test set of exactly 1494 images.

## 4. Training Reproduction
The actual training and fine-tuning workflow can be reproduced by running the provided scripts sequentially.
- **Initial Training:** Utilizes EfficientNet-B0, AdamW optimizer (learning rate 0.0001), `BCEWithLogitsLoss`, and dynamic positive-class weighting.
- **Fine-Tuning:** Unfreezes selected backbone layers, reduces learning rate to 0.00001, and selects the final checkpoint based on validation ROC-AUC.
*Note: The absence of exact explicit global seed handling means slight variations in model weights may occur during reproduction across different hardware environments.*

## 5. Evaluation Reproduction
Evaluation is conducted on the held-out test split (1494 samples). The evaluation metrics calculate Accuracy, Precision, Recall/Sensitivity, Specificity, F1, ROC-AUC, and the Confusion Matrix from the continuous sigmoid probability outputs against a strict 0.50 decision boundary. These reflect held-out test performance, not clinical validation.

## 6. Application Reproduction
To reproduce the Streamlit application inference, the trained model checkpoint is required at this exact local path: `models/best_finetuned_model.pth`. Because this checkpoint is not in Git, users must either reproduce the training process or manually place the supplied checkpoint here.

## 7. Offline Operation
"Offline operation" means that inference runs locally:
- The model checkpoint is loaded locally.
- Image processing and Grad-CAM calculations occur locally.
- Prediction history is stored locally.
- No network service is required for normal inference.
*Note: Offline inference does not mean offline installation; downloading the repository, packages, and datasets requires network access.*

## 8. Model Performance Limitations
The model achieves an ROC-AUC of 85.37%, an Accuracy of 68.47%, and a Recall of 90.88%. While it successfully identifies a large proportion of positive test examples at the 0.50 threshold, precision is considerably lower (39.53%), reflecting a substantial number of false positives (442). These are dataset-specific performance metrics on a held-out test set. The model is **not** clinically validated.

## 9. Dataset Limitations
- **Scope:** The model inherits the inherent biases of the HAM10000 dataset. 
- **Binary grouping:** The project simplifies highly nuanced dermatological conditions into two broad buckets, discarding original diagnostic granularity.
- **Generalization:** Performance on this specific dataset does not guarantee real-world clinical generalization across diverse demographics or diverse clinical image acquisition environments.

## 10. Threshold Limitations
The application currently uses a 0.50 decision threshold. Threshold analysis (from 0.10 to 0.90) confirms that adjusting the boundary changes the binary classification output, but ROC-AUC remains threshold-independent. 0.50 is utilized as an application decision threshold and was not evaluated or optimized as a clinical boundary.

## 11. Error Analysis Limitations
Error patterns observed on the test set indicate that `NV` and `BKL` dominate false positives (approx. 97.3%), while `MEL` dominates false negatives (approx. 82.8%). All false negatives belong to MEL, BCC, or AKIEC. Errors occur both near and farther from the 0.50 threshold. These observations describe visual model behavior but do not establish underlying medical or anatomical causes for the model's failures.

## 12. Reproducibility Limitations
- Raw data and the final checkpoint are excluded from Git. A fresh clone is not immediately inference-ready.
- The exact Python environment dependencies are pinned in `requirements.txt`. Deviating from these versions may alter reproduction.

## 13. Safety and Intended Use
This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions.
