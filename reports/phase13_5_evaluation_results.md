# Phase 13.5 — Evaluation Results

## 1. Evaluation Overview

The model was rigorously evaluated on an exclusively held-out test set designed to measure unbiased statistical performance. The test set contains exactly 1494 samples isolated via lesion-level grouping to prevent data leakage. Evaluation relies on continuous sigmoid probabilities produced by the model. 
Threshold-dependent metrics (such as Accuracy, Precision, and Recall) use the application's default 0.50 threshold. 
Conversely, the Receiver Operating Characteristic Area Under the Curve (ROC-AUC) evaluates the model's ranking and discrimination capability independently of any single decision threshold. 
*These metrics document computational performance on a specific dataset and do not constitute clinical validation.*

## 2. Final Test Results

The following verified results represent the model's performance on the 1494 held-out test samples at the 0.50 application threshold:

| Metric | Result |
|---|---:|
| Accuracy | 68.47% |
| Precision | 39.53% |
| Recall / Sensitivity | 90.88% |
| Specificity | 62.41% |
| F1-score | 55.10% |
| ROC-AUC | 85.37% |

**Confusion matrix:**

| | Predicted Non-malignant | Predicted Malignant-Suspicious |
|---|---:|---:|
| **Actual Non-malignant** | 734 | 442 |
| **Actual Malignant-Suspicious** | 29 | 289 |

**Explicit Confusion Counts:**
- TN = 734
- FP = 442
- FN = 29
- TP = 289

## 3. Interpreting the Metrics

- **Accuracy**: The proportion of all test samples (both non-malignant and malignant-suspicious) correctly classified at the 0.50 threshold.
- **Precision**: The proportion of positive (malignant-suspicious) predictions that actually belong to the positive class.
- **Recall/Sensitivity**: The proportion of actual positive-class test samples correctly classified as positive by the model.
- **Specificity**: The proportion of actual negative-class (non-malignant) test samples correctly classified as negative.
- **F1-score**: The harmonic mean of precision and recall, balancing both false positives and false negatives.
- **ROC-AUC**: The probability that the model will rank a randomly chosen positive sample higher than a randomly chosen negative sample, evaluated across all possible thresholds.

## 4. Confusion Matrix Analysis

At the selected 0.50 threshold, the confusion matrix shows 734 true negatives and 289 true positives, indicating successful classifications across the majority of the dataset. However, it also reveals a significant trade-off: 442 false positives against only 29 false negatives. The high recall rate (90.88%) inherently captures the majority of positive cases, but comes at the cost of significantly lower precision (39.53%), resulting in a high volume of false alarms. This threshold characterizes the application's current operating balance but does not imply the model is clinically appropriate or optimized.

## 5. ROC Analysis

**ROC-AUC = 0.8537**

The Receiver Operating Characteristic (ROC) curve plots the model's true positive rate against its false positive rate using continuous model probabilities. The Area Under the Curve (AUC) summarizes the model's overall statistical discrimination capability independently of the 0.50 application threshold. An AUC of 0.8537 indicates strong discriminatory ability on this test set, separate from the specific precision/recall trade-off dictated by the 0.50 cutoff.

*(For detailed visual context, refer to `reports/roc_curve.png`)*

## 6. Training and Validation Progress

The model's validation ROC-AUC progressed steadily throughout the training and fine-tuning phases. The metrics below trace the model's improvement over documented epochs.

| Phase | Epoch | Validation ROC-AUC |
|---|---|---:|
| Initial | 1 | 0.8158 |
| Initial | 2 | 0.8300 |
| Initial | 3 | 0.8357 |
| Fine-Tuning | 4 | 0.8443 |
| Fine-Tuning | 5 | 0.8562 |
| Fine-Tuning | 6 | 0.8621 |

Validation ROC-AUC improved across the recorded training and fine-tuning stages. The selected best checkpoint balances this discrimination capability against validation loss. This trend does not claim that indefinite training would necessarily yield infinite performance improvements, as models eventually overfit.

## 7. Baseline vs Fine-Tuned

The held-out test set evaluated both the initial baseline training and the subsequent fine-tuned checkpoint:

| Metric | Baseline | Fine-Tuned |
|---|---:|---:|
| Accuracy | 65.80% | 68.47% |
| Precision | 37.61% | 39.53% |
| Recall | 92.14% | 90.88% |
| Specificity | 58.67% | 62.41% |
| F1 | 53.42% | 55.10% |
| ROC-AUC | 82.50% | 85.37% |

**Observed changes:**
- Accuracy increased by 2.67 percentage points.
- Precision increased by 1.92 percentage points.
- Specificity increased by 3.74 percentage points.
- F1 increased by 1.68 percentage points.
- ROC-AUC increased by 2.87 percentage points.
- Recall decreased by 1.26 percentage points.

**Confusion Count changes:**
- Baseline: TN 690, FP 486, FN 25, TP 293
- Fine-tuned: TN 734, FP 442, FN 29, TP 289

The fine-tuned model produced a different operating balance. By slightly sacrificing recall (4 fewer true positives, 4 more false negatives), it significantly improved its ability to correctly identify true negatives (44 more true negatives, 44 fewer false positives), yielding higher overall discrimination (ROC-AUC).

## 8. Threshold Analysis

A threshold analysis was performed across decision boundaries from 0.10 to 0.90 to map classification dynamics.
- As the threshold increases, Precision typically rises, while Recall heavily declines.
- Consequently, Specificity improves at higher thresholds, severely suppressing the false-positive rate while sharply accelerating the false-negative rate.
- ROC-AUC remains unaffected because it calculates the integral of performance across all thresholds simultaneously.

The application's current threshold is exactly 0.50. This threshold is strictly an application configuration choice serving as a neutral mathematical midpoint; it is not presented as a clinically optimized threshold, nor does this project claim that threshold optimization produces a clinically optimal operating point.

## 9. Error Analysis

Total test errors = 471
- False positives = 442
- False negatives = 29

An analysis was conducted to map errors back to their original 7-class HAM10000 diagnostic identifiers.

**False Positives Distribution:**
- NV: 299
- BKL: 131
- VASC: 7
- DF: 5

**False Negatives Distribution:**
- MEL: 24
- BCC: 3
- AKIEC: 2

The classes NV (Melanocytic nevi) and BKL (Benign keratosis) account for approximately 97.3% of all false positives. MEL (Melanoma) accounts for approximately 82.8% of all false negatives. These patterns highlight statistical overlap within the computer vision feature space. These statistical distributions do not prove biological or medical causes for individual visual errors.

## 10. Error Probability Analysis

A probabilistic distribution analysis was conducted on the model's errors to understand classification confidence.

**False Positives (442 total):**
- 0.50–0.60: 129
- 0.60–0.70: 144
- 0.70–0.80: 112
- 0.80–0.90: 53
- 0.90–1.00: 4

*Observation:* Many false positives occur close to the 0.50 boundary. Some occur substantially farther from the threshold, though only a small fraction exceed 0.90.

**False Negatives (29 total):**
- 0.00–0.10: 1
- 0.10–0.20: 1
- 0.20–0.30: 5
- 0.30–0.40: 3
- 0.40–0.50: 19

*Observation:* Most false negatives cluster tightly between 0.40 and 0.50, though several are positioned substantially below 0.50. 
Errors occur both near and farther from the decision threshold, reiterating that individual model probabilities cannot be interpreted as medical certainty.

## 11. Representative Error Images

To qualify mathematical errors, specific representative test images were computationally extracted and grouped:
- **A — High-confidence false positives** (`error_grid_A_high_confidence_FP.png`)
- **B — Borderline false positives** (`error_grid_B_borderline_FP.png`)
- **C — Borderline false negatives** (`error_grid_C_borderline_FN.png`)
- **D — Low-probability false negatives** (`error_grid_D_low_probability_FN.png`)

These visual artifacts allow qualitative inspection of statistical model errors (e.g., assessing the impact of hair, shadows, or lighting on the CNN's feature maps). They do not offer, and should not be used for, medical interpretation of individual lesions.

## 12. What the Results Show

The empirical results present a balanced technical profile:
- The model achieved an ROC-AUC of 85.37% on the held-out test set.
- Recall at the 0.50 threshold was 90.88%.
- Specificity at the same threshold was 62.41%.
- Fine-tuning increased ROC-AUC and shifted the precision/recall/specificity balance compared to the baseline.
- False positives were heavily concentrated in the NV and BKL classes.
- False negatives were heavily concentrated in the MEL class.

## 13. What the Results Do NOT Show

- These results do not establish clinical validity.
- They do not establish performance on unseen external datasets.
- They do not establish suitability for clinical decision-making.
- They do not prove generalization to all skin-lesion images.
- Model probability is not medical certainty.

## 14. Reproducibility

Authoritative evaluation artifacts are systematically stored in the `reports/` directory. These include `test_predictions.csv`, `final_metrics_summary.csv`, `model_comparison.csv`, `threshold_analysis.csv`, `error_analysis.csv`, `training_history.csv`, and `finetuning_history.csv`. 

Because the raw dataset images and the heavy trained `.pth` model checkpoints are intentionally excluded from Git version control, fresh clones require independent, local setup of the data environment to explicitly reproduce these numbers via the provided test scripts.

## 15. Evaluation Artifacts

| Artifact | Purpose |
|---|---|
| `final_metrics_summary.csv` | Official record of all final test metrics (Accuracy, ROC-AUC, etc.). |
| `model_comparison.csv` | Side-by-side metric comparison of baseline vs fine-tuned epochs. |
| `threshold_analysis.csv` | Dataset detailing metric variation from 0.10 to 0.90 boundaries. |
| `error_analysis.csv` | Comprehensive log of every test set error mapped to true diagnostic labels. |
| `test_predictions.csv` | Log of probability outputs and predictions across all 1494 test images. |
| `training_history.csv` | Epoch-level documentation of the initial training loss and metrics. |
| `finetuning_history.csv` | Epoch-level documentation of the fine-tuning loss and metrics. |
| `roc_curve.png` | Visual plot calculating the 85.37% ROC-AUC curve. |
| `confusion_matrix.png` | Standardized 2x2 grid representing test set classifications. |
| `error_grids_*.png` | Visual aggregates of representative false positives/negatives. |

## 16. Future Evaluation Improvements

*The following considerations are documented strictly as future work:*
- External validation using entirely independent hospital datasets.
- Formal calibration analysis (e.g., Brier score) to align probability with actual occurrence.
- Class-balanced evaluation reporting.
- Advanced subgroup analysis based on demographic metadata if available.
- Expanding evaluation paradigms to true multiclass modeling scenarios.

## 17. Responsible Interpretation

> "This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions."
