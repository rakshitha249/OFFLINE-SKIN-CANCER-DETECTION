# Consolidated Model Evaluation Report

Subtitle: Offline Skin Lesion Classification — EfficientNet-B0

*This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions.*

## 2. EXECUTIVE SUMMARY
This report details the evaluation of a fine-tuned EfficientNet-B0 model on a binary classification task (Malignant-Suspicious vs. Non-malignant). On a strictly held-out test set of 1494 images, the model achieved an ROC-AUC of 85.37%. At the default decision threshold of 0.50, the model produced an Accuracy of 68.47%, Precision of 39.53%, Recall/Sensitivity of 90.88%, Specificity of 62.41%, and F1-score of 55.10%. These metrics indicate useful discriminatory capacity, but do not imply clinical validation.

## 3. EVALUATION SETUP
- **Task:** Binary classification
- **Positive Class:** Malignant-Suspicious
- **Negative Class:** Non-malignant
- **Test Samples:** 1494
- **Non-malignant Count:** 1176
- **Malignant-Suspicious Count:** 318
- **Decision Threshold:** 0.50

The evaluation was performed exclusively on a held-out test set that was kept strictly separate from the training phase. The project dataset utilizes lesion-level grouping to ensure that multiple images of the exact same physical lesion do not straddle training and testing boundaries, avoiding data leakage. 

## 4. TRAINING AND VALIDATION RESULTS
The model was trained over six total epochs (three initial training epochs, followed by three fine-tuning epochs). 

| Epoch | Train Loss | Validation Loss | Train Accuracy | Validation Accuracy | Train F1 | Validation F1 | Validation ROC-AUC |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 (Initial) | 1.037 | 0.938 | 61.58% | 62.67% | 41.95% | 47.55% | 81.58% |
| 2 (Initial) | 0.932 | 0.873 | 69.92% | 65.64% | 50.14% | 49.52% | 83.01% |
| 3 (Initial) | 0.888 | 0.855 | 71.19% | 63.27% | 51.32% | 48.90% | 83.57% |
| 4 (Fine-tune) | 0.851 | 0.801 | 71.55% | 67.54% | 52.57% | 51.04% | 84.44% |
| 5 (Fine-tune) | 0.813 | 0.763 | 71.69% | 69.59% | 53.25% | 52.47% | 85.63% |
| 6 (Fine-tune) | 0.792 | 0.765 | 72.79% | 66.82% | 54.26% | 50.97% | 86.22% |

*Note: Train ROC-AUC was not historically logged during the training runs.*

Throughout the six epochs, validation loss generally decreased and validation ROC-AUC improved sequentially, demonstrating that the fine-tuning process was productive. Epoch 6 showed a very slight validation-loss increase (0.765) compared to Epoch 5 (0.763), though ROC-AUC still marginally improved. While validation metrics remained stable, we cannot definitively claim the absolute absence of overfitting. Historical progress can be visualized in `reports/training_validation_loss.png` and `reports/validation_roc_auc.png`.

## 5. FINAL TEST-SET PERFORMANCE
The following table reflects held-out test-set results at the default 0.50 threshold:

| Metric | Result |
| :--- | :--- |
| Accuracy | 68.47% |
| Precision | 39.53% |
| Recall/Sensitivity | 90.88% |
| Specificity | 62.41% |
| F1 | 55.10% |
| ROC-AUC | 85.37% |

## 6. CONFUSION MATRIX ANALYSIS

| | Predicted Non-malignant | Predicted Malignant-Suspicious |
|---|---:|---:|
| Actual Non-malignant | 734 | 442 |
| Actual Malignant-Suspicious | 29 | 289 |

- TN = 734
- FP = 442
- FN = 29
- TP = 289

The sum of the matrix quadrants equals the complete test set count (734 + 442 + 29 + 289 = 1494). The confusion matrix reveals a high sensitivity (few false negatives) offset by a very large volume of false positive predictions, highlighting a strong bias toward predicting the malignant class under uncertainty. 

## 7. ROC ANALYSIS
The final fine-tuned model achieved a held-out test set **ROC-AUC of 0.8537**. 
ROC-AUC evaluates the model's ability to rank positive and negative examples globally across all possible classification thresholds. Therefore, it does not depend on one fixed threshold. The resulting curve and AUC can be reviewed in `reports/roc_curve.png`.

## 8. BASELINE VS FINE-TUNED MODEL
Comparison derived from `reports/model_comparison.csv`:

| Metric | Baseline | Fine-tuned | Change |
| :--- | :--- | :--- | :--- |
| Accuracy | 65.80% | 68.47% | +2.67 pp |
| Precision | 37.61% | 39.53% | +1.92 pp |
| Recall | 92.14% | 90.88% | -1.26 pp |
| Specificity | 58.67% | 62.41% | +3.74 pp |
| F1 | 53.42% | 55.10% | +1.68 pp |
| ROC-AUC | 82.50% | 85.37% | +2.87 pp |

Fine-tuning the EfficientNet-B0 backbone improved several crucial metrics—including ROC-AUC, accuracy, specificity, precision, and F1—while recall decreased slightly. These changes represent a favorable structural improvement over the baseline state.

## 9. THRESHOLD ANALYSIS
As demonstrated in `reports/threshold_analysis.csv`, manipulating the decision threshold profoundly changes the discrete output metrics:
- Lower thresholds aggressively increase the number of positive predictions, generally increasing recall while severely reducing specificity (and inflating False Positive Rates).
- Higher thresholds generally increase specificity (reducing false alarms) at the severe cost of reducing recall (inflating False Negative Rates).
- Threshold 0.50 is utilized as the current project evaluation baseline.

**Important:** This analysis does NOT establish 0.50 as a clinically optimal threshold. Threshold selection for any hypothetical deployment should ideally be derived from an appropriate validation-set decision policy, evaluating risk tolerance, rather than being optimized retroactively on the test set. (Note again that ROC-AUC remains threshold-independent). Visualizations are available in `reports/threshold_vs_metrics.png`, `reports/threshold_vs_error_rates.png`, and `reports/threshold_confusion_counts.png`.

## 10. ERROR ANALYSIS
Total recorded errors in the test set equal 471 (442 False Positives and 29 False Negatives).

**False Positives by Original Class:**
- NV: 299
- BKL: 131
- VASC: 7
- DF: 5

*NV and BKL account for 430/442 (approximately 97.3%) of all false positives.*

**False Negatives by Original Class:**
- MEL: 24
- BCC: 3
- AKIEC: 2

*MEL accounts for 24/29 (approximately 82.8%) of all false negatives.*

**Probability Distribution Statistics:**
- TP mean = 0.7476
- TN mean = 0.2125
- FP mean = 0.6717
- FN mean = 0.3892

The vast majority of the model's critical misses are borderline; 19 out of 29 false negatives fall exactly between probability 0.40 and 0.50. Conversely, the model is rarely confidently wrong about benign lesions, with only 4 false positives generating a probability above 0.90. 

## 11. REPRESENTATIVE ERROR IMAGE ANALYSIS
20 representative error images were selected entirely deterministically in `reports/selected_error_images.csv` and rendered into four corresponding visual grids:
- `reports/error_grid_A_high_confidence_FP.png` (5 high-confidence FPs)
- `reports/error_grid_B_borderline_FP.png` (5 borderline FPs)
- `reports/error_grid_C_borderline_FN.png` (5 borderline FNs)
- `reports/error_grid_D_low_probability_FN.png` (5 low-probability FNs)

Visual observations across these grids highlight noticeable variance, including pigmentation variation, internal color variation, differences in lesion size and framing, surrounding skin/background differences, hair/artifacts, and variation in apparent shape. 
*These characteristics may contribute to visual variability encountered by the model, but this visual inspection does not establish causality.*

## 12. MODEL LIMITATIONS
- Evaluation remains strictly dataset-specific.
- No external-dataset validation was performed.
- No clinical validation was performed.
- Severe class imbalance exists.
- Relatively small representation of some original diagnostic classes limits sub-class certainty.
- Discrete metrics exhibit heavy threshold dependence.
- Image acquisition variability likely impacts predictions.
- A high false-positive burden limits usability.
- Remaining false-negative cases highlight significant unresolved risk.
- Model probabilities are statistical outputs, not statements of medical certainty.
- These results cannot establish clinical diagnostic performance.

## 13. REPRODUCIBILITY AND ARTIFACTS
The following evaluation artifacts were verifiably generated and retained:
- `test_predictions.csv`
- `model_comparison.csv`
- `threshold_analysis.csv`
- `error_analysis.csv`
- `selected_error_images.csv`
- `confusion_matrix.png`
- `roc_curve.png`
- training/validation plots
- threshold plots
- error-analysis plots
- error-analysis grids
- `final_metrics_summary.csv`
- `final_metrics_summary.md`
- `evaluation_artifact_verification.md`

Phase 8.9A previously verified these evaluation artifacts conducting 35 checks, returning 35 PASS, 0 WARNING, and 0 FAIL. 

## 14. KEY FINDINGS
- ROC-AUC = 85.37% on the held-out test set.
- Recall = 90.88%.
- Specificity = 62.41%.
- Fine-tuning improved ROC-AUC from 82.50% to 85.37%.
- The model produced 442 FP and 29 FN at threshold 0.50.
- NV and BKL account for approximately 97.3% of FPs.
- MEL accounts for approximately 82.8% of FNs.

## 15. OVERALL CONCLUSION
The fine-tuned EfficientNet-B0 demonstrates useful discriminatory performance on this held-out test set. The targeted fine-tuning process improved overall ROC-AUC relative to the baseline architecture. The model achieved a high recall at the selected 0.50 threshold, but also produced a substantial number of false positives. Furthermore, deep error analysis reveals aggressive class-specific patterns (specifically with NV, BKL, and MEL) in the current dataset. These results are highly useful for understanding the current prototype's behavior; however, further validation on external datasets and appropriate clinical evaluation would be strictly required before any real-world medical use could be considered.

## 16. SAFETY DISCLAIMER
This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions.
