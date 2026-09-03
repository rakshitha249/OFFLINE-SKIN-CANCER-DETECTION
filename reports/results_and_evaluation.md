# Results and Evaluation

## 1. Evaluation Overview
These results represent the final model evaluation performed on the project's held-out test set after the completion of initial training and fine-tuning. The evaluation was conducted on exactly 1494 images (1176 negative samples, 318 positive samples). The binary classification results are calculated using a decision threshold of 0.50.

## 2. Final Test Metrics

| Metric | Result |
|---|---:|
| Accuracy | 68.47% |
| Precision | 39.53% |
| Recall / Sensitivity | 90.88% |
| Specificity | 62.41% |
| F1 Score | 55.10% |
| ROC-AUC | 85.37% |

- **Accuracy:** The overall proportion of correct predictions across both classes.
- **Precision:** The proportion of positive predictions that were actually positive.
- **Recall / Sensitivity:** The proportion of actual positive examples that the model correctly identified.
- **Specificity:** The proportion of actual negative examples that the model correctly identified.
- **F1 Score:** The harmonic mean of precision and recall.
- **ROC-AUC:** A threshold-independent metric summarizing the model's ability to rank positive and negative examples.

## 3. Confusion Matrix

| | Predicted Non-malignant | Predicted Malignant-Suspicious |
|---|---:|---:|
| Actual Non-malignant | 734 | 442 |
| Actual Malignant-Suspicious | 29 | 289 |

- TN = 734
- FP = 442
- FN = 29
- TP = 289

See visual confusion matrix: [Confusion Matrix](confusion_matrix.png)

## 4. ROC Curve

ROC-AUC = 85.37%

The ROC-AUC summarizes discrimination across all possible classification thresholds, independent of the 0.50 decision threshold.

See ROC Curve plot: [ROC Curve](roc_curve.png)

## 5. Baseline vs Fine-Tuned Model

**Baseline Model Results:**
- Accuracy = 65.80%
- Precision = 37.61%
- Recall = 92.14%
- Specificity = 58.67%
- F1 = 53.42%
- ROC-AUC = 82.50%

**Fine-Tuned Model Results:**
- Accuracy = 68.47%
- Precision = 39.53%
- Recall = 90.88%
- Specificity = 62.41%
- F1 = 55.10%
- ROC-AUC = 85.37%

**Changes:**
- Accuracy: +2.67 percentage points
- Precision: +1.92 percentage points
- Recall: -1.26 percentage points
- Specificity: +3.74 percentage points
- F1: +1.68 percentage points
- ROC-AUC: +2.87 percentage points
- TN: +44
- FP: -44
- FN: +4
- TP: -4

Fine-tuning improved several overall test metrics, including ROC-AUC, accuracy, precision, specificity, and F1, while recall decreased slightly.

See CSV details: [model_comparison.csv](model_comparison.csv)

## 6. Threshold Analysis

The evaluation analyzed classification thresholds ranging from 0.10 through 0.90. The threshold determines the binary classification decision output. The application currently uses a 0.50 decision threshold. Note that ROC-AUC is threshold-independent.

*The 0.50 threshold is an application decision threshold. It is not presented as a clinically optimized threshold.*

See analysis details: [threshold_analysis.csv](threshold_analysis.csv)

## 7. Error Analysis

Total test set errors = 471
False positives = 442
False negatives = 29

**Original-class distribution for False Positives:**
- NV: 299 FP
- BKL: 131 FP
- VASC: 7 FP
- DF: 5 FP

**Original-class distribution for False Negatives:**
- MEL: 24 FN
- BCC: 3 FN
- AKIEC: 2 FN

**Important findings:**
- `NV` and `BKL` together account for approximately 97.3% of false positives.
- `MEL` accounts for approximately 82.8% of false negatives.
- Errors occur both near and farther from the 0.50 threshold.
- False positives are not limited to near-threshold cases.
- False negatives include both borderline and lower-probability cases.

These are model error patterns in this specific test set.

See detailed error analysis report: [Error Analysis Report](error_analysis_report.md)

## 8. Probability / Threshold Behavior

**Mean estimated probabilities:**
- True positives: mean probability ≈ 0.7476
- True negatives: mean probability ≈ 0.2125
- False positives: mean probability ≈ 0.6717
- False negatives: mean probability ≈ 0.3892

**Observations:**
- 19 of 29 false negatives were in the 0.40–0.50 probability range.
- Only 4 false positives were above 0.90.

These descriptive statistics summarize the threshold behavior.

## 9. What the Results Show

- The fine-tuned model achieved ROC-AUC of 0.8537 on the held-out test set.
- The model identified a large proportion of positive test examples at the 0.50 threshold, reflected by 90.88% recall.
- Precision was lower than recall, reflecting a substantial number of false positives.
- Fine-tuning improved ROC-AUC, specificity, accuracy, precision, and F1 relative to the baseline while slightly reducing recall.
- Errors are concentrated in particular original classes.

## 10. Limitations

- Held-out test performance is not clinical validation.
- Results are dataset-specific (HAM10000).
- Binary grouping simplifies the original seven-class problem.
- False positives and false negatives remain.
- Threshold 0.50 is an application decision threshold; it was not clinically optimized.
- No external clinical validation has been performed.
- Real-world generalization is not established.
- Image acquisition variability may affect model behavior.
- Dataset and model checkpoints are not included in Git.

## 11. Detailed Reports

- [Consolidated Evaluation Report](consolidated_evaluation_report.md)
- [Final Metrics Summary (Markdown)](final_metrics_summary.md)
- [Error Analysis Report](error_analysis_report.md)
- [Threshold Analysis CSV](threshold_analysis.csv)
- [Model Comparison CSV](model_comparison.csv)
- [Evaluation Artifact Verification](evaluation_artifact_verification.md)
