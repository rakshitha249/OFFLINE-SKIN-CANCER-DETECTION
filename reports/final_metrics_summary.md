# Final Model Evaluation Summary

## 1. Evaluation Setup
- Model: Fine-tuned EfficientNet-B0
- Task: binary classification
- Positive class: Malignant-Suspicious
- Negative class: Non-malignant
- Test set: 1494 samples
- Non-malignant: 1176
- Malignant-Suspicious: 318
- Decision threshold: 0.50
- Evaluation performed on the held-out test set

## 2. Final Test Metrics

| Metric | Value |
| :--- | :--- |
| Accuracy | 68.47% |
| Precision | 39.53% |
| Recall/Sensitivity | 90.88% |
| Specificity | 62.41% |
| F1 | 55.10% |
| ROC-AUC | 85.37% |

## 3. Confusion Matrix

| | Predicted Non-malignant | Predicted Malignant-Suspicious |
|---|---:|---:|
| Actual Non-malignant | 734 | 442 |
| Actual Malignant-Suspicious | 29 | 289 |

TN = 734
FP = 442
FN = 29
TP = 289

## 4. Baseline vs Fine-tuned

| Metric | Baseline | Fine-tuned | Change |
| :--- | :--- | :--- | :--- |
| Accuracy | 65.80% | 68.47% | +2.67 pp |
| Precision | 37.61% | 39.53% | +1.92 pp |
| Recall | 92.14% | 90.88% | -1.26 pp |
| Specificity | 58.67% | 62.41% | +3.74 pp |
| F1 | 53.42% | 55.10% | +1.68 pp |
| ROC-AUC | 82.50% | 85.37% | +2.87 pp |

## 5. Threshold Context
- metrics such as accuracy, precision, recall, specificity and F1 depend on the selected threshold
- ROC-AUC is threshold-independent because it evaluates ranking across thresholds
- 0.50 is the current project evaluation threshold
- this analysis does NOT establish 0.50 as a clinically optimal threshold

## 6. Error Analysis Summary
- FP = 442
- FN = 29
- NV = 299 FP
- BKL = 131 FP
- VASC = 7 FP
- DF = 5 FP
- MEL = 24 FN
- BCC = 3 FN
- AKIEC = 2 FN

- NV + BKL = 430/442 = approximately 97.3% of false positives
- MEL = 24/29 = approximately 82.8% of false negatives

## 7. Interpretation
- the fine-tuned model achieved ROC-AUC of approximately 0.8537 on this held-out test set
- recall was 90.88%
- specificity was 62.41%
- the model produced substantially more false positives than false negatives at threshold 0.50
- the results describe performance on this particular held-out dataset

## 8. Limitations
- evaluation is dataset-specific
- class imbalance exists
- some original diagnostic classes have relatively small sample counts
- threshold changes alter classification metrics
- image acquisition variability may affect predictions
- no external-dataset validation was performed
- no clinical validation was performed

## 9. Key Numbers
Results on the held-out test set:
- Test samples: 1494
- ROC-AUC: 85.37%
- Accuracy: 68.47%
- Recall/Sensitivity: 90.88%
- Specificity: 62.41%
- Precision: 39.53%
- F1: 55.10%
- FP: 442
- FN: 29
