# Phase 13.4 — Model & Training Documentation

## 1. Model Development Overview

The model development process follows a structured, sequential pipeline designed for binary classification of skin lesions:
Dataset ingestion → Preprocessing → Binary label mapping → Grouped splitting → Initial model training → Fine-tuning → Validation monitoring → Best checkpoint selection → Held-out test evaluation.

This process ensures that the model is trained with appropriately isolated data and evaluated strictly on unseen images.

## 2. Dataset

The project utilizes the public HAM10000 / ISIC dataset. 
- **Original Scale**: The dataset contains 10,015 dermatoscopic images.
- **Original Classes**: The dataset initially classifies lesions into seven distinct diagnostic categories.
- **Data Structure**: It consists of a metadata CSV linking image filenames to diagnostic labels and demographic data, alongside the actual image files.
- **Lesion ID**: A crucial piece of metadata is the `lesion_id`, which tracks multiple photographic captures of the exact same physical skin lesion. This `lesion_id` is essential for grouped splitting to prevent identical lesions from appearing in both training and test sets.

## 3. Binary Classification Setup

To adapt the dataset for this research prototype, the original seven clinical classes are mapped into a binary schema:

**Label 0 — Non-malignant:**
- NV (Melanocytic nevi)
- BKL (Benign keratosis-like lesions)
- DF (Dermatofibroma)
- VASC (Vascular lesions)

**Label 1 — Malignant-Suspicious:**
- MEL (Melanoma)
- BCC (Basal cell carcinoma)
- AKIEC (Actinic keratoses and intraepithelial carcinoma)

*Note: This binary grouping is specific to this research prototype's statistical modeling goals and is not equivalent to a clinical diagnosis or medical severity index.*

## 4. Dataset Splitting

The project splits the dataset into three distinct partitions:
- **Distribution**: Approximately 70% Train, 15% Validation, and 15% Test.
- **Methodology**: `GroupShuffleSplit` is utilized, grouping explicitly by `lesion_id`.
- **Purpose**: Grouping prevents multiple photographic angles of the same physical lesion from crossing split boundaries (e.g., being in both the training set and the test set). While this greatly reduces artificial data leakage and inflated evaluation metrics, it does not eliminate underlying dataset bias (such as skin tone, lighting, or institutional acquisition markers).

## 5. Image Preprocessing

Input images undergo standardized transformations before entering the model:
- **Image Resizing**: All images are resized to 224x224 pixels.
- **Tensor Conversion**: Images are converted to PyTorch tensors.
- **Normalization**: Standard ImageNet normalization is applied (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).

*Training vs. Evaluation Differences:*
During the training phase, data augmentation (e.g., random horizontal/vertical flips, rotations, and color jitter) is applied to artificially increase dataset variance and combat class imbalance. During validation and test evaluation, only resizing, tensor conversion, and normalization are applied to ensure deterministic evaluation.

## 6. Model Architecture

- **Backbone**: The model utilizes an EfficientNet-B0 architecture.
- **Initialization**: It is initialized with pre-trained ImageNet weights.
- **Classifier Modification**: The final fully connected classification head is replaced with a linear layer that outputs a single feature logit.
- **Binary Output**: This single logit represents the raw model prediction.
- **Sigmoid Interpretation**: During inference, a Sigmoid activation function is applied to the logit to squash the output into a continuous estimated probability range between 0 and 1.

## 7. Initial Training

The initial training phase optimized the modified classification head and updated the pre-trained weights. The recorded history demonstrates a steady decrease in loss and an improvement in validation ROC-AUC across three epochs.

| Epoch | Train Loss | Val Loss | Train Acc | Val Acc | Train Prec | Val Prec | Train Rec | Val Rec | Train F1 | Val F1 | Val ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0370 | 0.9378 | 0.6158 | 0.6267 | 0.2967 | 0.3200 | 0.7157 | 0.9244 | 0.4195 | 0.4754 | 0.8158 |
| 2 | 0.9323 | 0.8733 | 0.6992 | 0.6563 | 0.3695 | 0.3386 | 0.7798 | 0.9208 | 0.5014 | 0.4951 | 0.8300 |
| 3 | 0.8876 | 0.8549 | 0.7119 | 0.6326 | 0.3816 | 0.3280 | 0.7827 | 0.9604 | 0.5131 | 0.4890 | 0.8357 |

## 8. Fine-Tuning

Following the initial training, a fine-tuning phase was executed. This stage typically involves adjusting learning rates or selectively unfreezing deeper layers of the EfficientNet-B0 backbone to allow the model to learn domain-specific skin lesion features. *(Specific layer-freezing configurations are implemented dynamically in the source codebase).*

| Fine-Tune Epoch | Train Loss | Val Loss | Train Acc | Val Acc | Train Prec | Val Prec | Train Rec | Val Rec | Train F1 | Val F1 | Val ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 (Epoch 4) | 0.8505 | 0.8007 | 0.7155 | 0.6754 | 0.3884 | 0.3525 | 0.8129 | 0.9244 | 0.5257 | 0.5104 | 0.8443 |
| 2 (Epoch 5) | 0.8130 | 0.7631 | 0.7169 | 0.6958 | 0.3917 | 0.3674 | 0.8313 | 0.9172 | 0.5325 | 0.5246 | 0.8562 |
| 3 (Epoch 6) | 0.7921 | 0.7650 | 0.7279 | 0.6682 | 0.4025 | 0.3493 | 0.8321 | 0.9424 | 0.5426 | 0.5097 | 0.8621 |

## 9. Training Progress

The combined training progression shows a consistent improvement in the model's discriminative capability:
- **Epoch 1**: Train loss 1.0370, Val loss 0.9378, Val ROC-AUC 0.8158
- **Epoch 2**: Train loss 0.9323, Val loss 0.8733, Val ROC-AUC 0.8300
- **Epoch 3**: Train loss 0.8876, Val loss 0.8549, Val ROC-AUC 0.8357
- **Fine-tuning Epoch 4**: Train loss 0.8505, Val loss 0.8007, Val ROC-AUC 0.8443
- **Fine-tuning Epoch 5**: Train loss 0.8130, Val loss 0.7631, Val ROC-AUC 0.8562
- **Fine-tuning Epoch 6**: Train loss 0.7921, Val loss 0.7650, Val ROC-AUC 0.8621

The trend demonstrates steady optimization without definitive signs of severe overfitting, as validation ROC-AUC consistently improves alongside decreasing training loss.

## 10. Model Selection

The project utilizes validation ROC-AUC as the primary metric for model selection. The checkpoint achieving the highest validation ROC-AUC during the training and fine-tuning phases is saved locally as `models/best_finetuned_model.pth`. This selected checkpoint is subsequently used for the final, unbiased evaluation on the held-out test set.

## 11. Test Evaluation

The selected fine-tuned model was evaluated on the exclusively held-out test set (1494 samples). These results represent statistical performance on this specific dataset partition and do not represent clinical performance.

| Metric | Value |
|---|---:|
| Accuracy | 68.47% |
| Precision | 39.53% |
| Recall/Sensitivity | 90.88% |
| Specificity | 62.41% |
| F1-score | 55.10% |
| ROC-AUC | 85.37% |

**Confusion Matrix (at 0.50 threshold):**
- True Negatives (TN): 734
- False Positives (FP): 442
- False Negatives (FN): 29
- True Positives (TP): 289

*Interpretation*: ROC-AUC is a threshold-independent metric describing overall separability. Accuracy, Precision, Recall, Specificity, and F1 are threshold-dependent metrics evaluated here at the application's default 0.50 threshold.

## 12. Baseline vs Fine-Tuned

The held-out test set was used to verify the impact of fine-tuning compared to the baseline initial training epoch:

| Metric | Baseline | Fine-tuned | Change |
|---|---|---|---|
| Accuracy | 65.80% | 68.47% | Increased |
| Precision | 37.61% | 39.53% | Increased |
| Recall | 92.14% | 90.88% | Decreased slightly |
| Specificity | 58.67% | 62.41% | Increased |
| F1 | 53.42% | 55.10% | Increased |
| ROC-AUC | 82.50% | 85.37% | Increased |

Fine-tuning successfully increased overall Accuracy, Precision, Specificity, F1, and ROC-AUC. It shifted the balance of predictions slightly, yielding a minor decrease in Recall while significantly reducing false positives (increasing Specificity).

## 13. Threshold Analysis

A threshold analysis was performed across decision boundaries ranging from 0.10 to 0.90. The analysis confirms that threshold-dependent classification metrics shift predictably as the boundary changes, whereas the holistic ROC-AUC remains constant. The current application is configured to use the mathematical center (0.50) as the decision threshold. This is strictly a software configuration choice, not a clinically optimized operating point.

## 14. Error Analysis

Statistical error analysis isolates the model's failure profiles on the test set:
- **False Positives (442)**: The model frequently misclassified benign lesions as malignant-suspicious. The original `NV` (nevi) and `BKL` classes strongly dominate these false positive predictions.
- **False Negatives (29)**: The model occasionally missed malignant lesions, with the `MEL` (melanoma) class dominating the false negatives.

This analysis is used to identify statistical dataset overlapping and guides future machine learning improvements. No medical causes are inferred from these individual computational errors.

## 15. Reproducibility

The repository supports reproducibility through pinned dependencies (`requirements.txt`), documented dataset split algorithms (`create_splits.py`), provided training scripts, and recorded CSV histories.
**Crucially:** 
- The raw HAM10000 dataset is not committed.
- Processed dataset split files are not committed.
- The `.pth` trained checkpoint is not committed.
A fresh clone requires the user to independently download the raw dataset and execute the data preparation and training scripts locally to fully reproduce the model checkpoint.

## 16. Model Limitations

The documented limitations of this model include:
- The enforced binary grouping obscures the nuance of the original seven-class diagnostics.
- Heavy class imbalance within the original dataset impacts precision.
- The model exhibits a high volume of false positives, particularly confusing NV/BKL lesions.
- Evaluation is dataset-specific (HAM10000 only) and lacks external validation.
- Test-set performance is limited, and the model probabilities do not equal medical certainty.
- Variability in image acquisition (lighting, zoom, skin tone) negatively impacts inference.
- **There is no clinical validation.**

## 17. Future ML Improvements

Technically reasonable future machine learning enhancements include:
- Expanding the output head to handle true multiclass classification.
- Applying dynamic class-balanced focal loss during training.
- Integrating external datasets for robust external validation.
- Performing formal probability calibration.
- Implementing hyperparameter optimization sweeps.
- Exploring heavier augmentation strategies (e.g., MixUp or CutMix).
- Comparing multiple architecture backbones (e.g., ResNet50, ConvNeXt).
- Developing improved explainability evaluation metrics beyond Grad-CAM.

## 18. Technical Summary

The end-to-end model development workflow flows sequentially:
Dataset ingestion → Binary labeling mapping → Lesion-grouped dataset split → EfficientNet-B0 initialization → Initial parameter training → Deeper network fine-tuning → Validation-based ROC-AUC checkpoint selection → Authoritative held-out test evaluation → Error analysis → Final deployment for local Streamlit inference.
