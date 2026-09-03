# Dataset and Methodology

## 1. Dataset Overview
This project utilizes the publicly available HAM10000 / ISIC dataset. The full dataset consists of 10,015 images representing various skin lesion types. 

## 2. Original Dataset Classes
The original HAM10000 dataset provides seven granular diagnostic classes:
- **NV**: Melanocytic nevi
- **BKL**: Benign keratosis-like lesions
- **MEL**: Melanoma
- **BCC**: Basal cell carcinoma
- **AKIEC**: Actinic keratoses and intraepithelial carcinoma / Bowen's disease
- **VASC**: Vascular lesions
- **DF**: Dermatofibroma

## 3. Binary Label Definition
For the purposes of this AI research and educational prototype, the seven original classes were mapped into a binary machine-learning target:

| Original Class | Binary Label |
|---|---|
| NV | Non-malignant (0) |
| BKL | Non-malignant (0) |
| DF | Non-malignant (0) |
| VASC | Non-malignant (0) |
| MEL | Malignant-Suspicious (1) |
| BCC | Malignant-Suspicious (1) |
| AKIEC | Malignant-Suspicious (1) |

*Note: This mapping defines the project's machine-learning target and allows the model to produce a single statistical output. It is not a clinical diagnostic grouping.*

## 4. Metadata and Lesion IDs
The dataset metadata includes an `image_id` for every unique image and a `lesion_id` for the corresponding physical lesion. Because multiple images were sometimes taken of the exact same physical lesion, the `lesion_id` is a critical variable for preventing data leakage during dataset splitting.

## 5. Dataset Splitting
To prevent data leakage, the project uses `GroupShuffleSplit` (from `scikit-learn`) using `lesion_id` as the grouping variable. This strictly ensures that all images associated with the same physical lesion remain exclusively in one split (Train, Validation, or Test). This reduces the possibility of leakage between splits, though it cannot eliminate all inherent dataset biases.

The dataset was sequentially split:
- **Training:** ~70% of lesion groups
- **Validation:** ~15% of lesion groups
- **Test:** ~15% of lesion groups

## 6. Held-Out Test Set
The final held-out test set contains exactly **1494 images**. This dataset is strictly isolated and used exclusively for the final evaluation of the trained model, ensuring an unbiased assessment of performance against unseen data.

## 7. Data Preprocessing

### Training
During training and fine-tuning, images undergo dynamic augmentation to increase visual variety and prevent overfitting:
- Resize to 224x224 pixels
- RandomHorizontalFlip
- RandomVerticalFlip
- RandomRotation (up to 20 degrees)
- ColorJitter (brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1)
- ToTensor
- ImageNet Normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

### Validation
Validation images undergo strictly deterministic preprocessing:
- Resize to 224x224 pixels
- ToTensor
- ImageNet Normalization

### Test / Inference
The held-out test set and the Streamlit inference application use the exact same deterministic preprocessing pipeline as validation:
- Resize to 224x224 pixels
- ToTensor
- ImageNet Normalization

## 8. Training Methodology
- **Architecture:** EfficientNet-B0 (with a customized binary classification head replacing the final linear layer).
- **Epochs:** 3 initial training epochs.
- **Optimizer:** AdamW (Learning Rate: 0.0001, Weight Decay: 0.0001).
- **Loss Function:** `BCEWithLogitsLoss` utilizing dynamic positive class weighting to counteract the dataset's severe class imbalance.
- **Batch Size:** 16.
- **Checkpointing:** The model with the highest Validation ROC-AUC was saved.

## 9. Fine-Tuning Methodology
- **Strategy:** Using the best checkpoint from initial training, the final feature layers of the EfficientNet-B0 backbone were unfrozen to allow targeted adaptation to skin lesion concepts.
- **Epochs:** 3 fine-tuning epochs.
- **Optimizer:** AdamW with a reduced Learning Rate of 0.00001 to prevent catastrophic forgetting.
- **Checkpoint Selection:** The fine-tuned checkpoint was evaluated using Validation ROC-AUC, and the best-performing epoch was saved as `models/best_finetuned_model.pth`.

## 10. Model Output and Threshold
The model inference path operates as follows:
1. The binary classification head produces a raw model logit.
2. The logit is passed through a Sigmoid function to generate an estimated model probability (0.0 to 1.0).
3. The estimated model probability is evaluated against a strict **0.50 decision threshold**.
4. Values >= 0.50 generate a "Malignant-Suspicious" binary model prediction; values < 0.50 generate a "Non-malignant" prediction.

*The 0.50 threshold is an application decision boundary; it is not a clinically optimized threshold.*

## 11. Evaluation Methodology
The held-out test set (1494 images) was evaluated using the final fine-tuned checkpoint. The authoritative evaluation metrics are:
- **Accuracy:** 68.47%
- **Precision:** 39.53%
- **Recall/Sensitivity:** 90.88%
- **Specificity:** 62.41%
- **F1:** 55.10%
- **ROC-AUC:** 85.37%

**Confusion Matrix (Threshold 0.50):**
- True Negatives (TN) = 734
- False Positives (FP) = 442
- False Negatives (FN) = 29
- True Positives (TP) = 289

*These metrics represent statistical performance on a specific dataset and do not constitute clinical validation.*

## 12. Error Analysis
A rigorous error analysis evaluated the test set predictions:
- **False Positives (442):** Dominated by `NV` and `BKL`. Together, `NV` + `BKL` account for approximately 97.3% of all false positives.
- **False Negatives (29):** Dominated by `MEL`, which accounts for approximately 82.8% of all false negatives.
- Errors occurred both near the 0.50 threshold and farther from it.

Visual inspection was conducted for exploratory model-behavior analysis rather than clinical interpretation. For full findings, see [Error Analysis Report](error_analysis_report.md).

## 13. Threshold Analysis
Threshold analysis evaluated the model's metrics across boundaries ranging from 0.10 to 0.90. This established that varying the threshold profoundly affects classification decisions (trading sensitivity for specificity). The ROC-AUC metric remains threshold-independent. The application currently utilizes 0.50 as a mathematical baseline, not a clinically optimized threshold.

## 14. Methodology Limitations
The methodology is constrained by several documented limitations:
- The binary grouping simplifies the original, highly nuanced seven-class problem.
- Severe class imbalance heavily influenced initial metrics and necessitated weight adjustments.
- Results represent dataset-specific characteristics (HAM10000), and test performance does not establish real-world clinical generalization.
- The 0.50 threshold selection is a mathematical baseline and is not clinically optimized.
- Dataset and image acquisition variability continue to produce noticeable model errors (high false-positive burden).
- The raw dataset and the trained checkpoint are excluded from the repository to manage cloning footprint size, requiring manual reproduction steps.
