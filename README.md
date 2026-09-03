# Offline Skin Cancer Detection

## Overview
This project is an offline AI research and educational prototype for binary skin-lesion image classification. 

**Important:** It is NOT a medical diagnostic device. Model probabilities represent statistical outputs from the trained neural network, not measures of medical certainty. It should not be used to make clinical decisions.

## Features
- Offline image analysis via local web interface
- Binary classification (Malignant-Suspicious vs. Non-malignant)
- Malignant-suspicious probability & Non-malignant probability scoring
- Confidence interpretation
- Image quality assessment
- Grad-CAM explainability for visual feature highlighting
- Prediction history session state
- Evaluation and error-analysis artifacts generation

## Model
- **Architecture:** EfficientNet-B0
- **Task:** Fine-tuned for binary classification
- **Output:** Sigmoid probability
- **Classification Threshold:** 0.50 (Currently active project threshold)

*(Note: The model is not clinically validated.)*

## Dataset
This project uses the publicly available HAM10000 / ISIC dataset.
The dataset originally features seven diagnostic classes: `AKIEC`, `BCC`, `BKL`, `DF`, `MEL`, `NV`, `VASC`.

For this project, these are mapped into a binary schema:
- **Class 0 (Non-malignant):** `NV`, `BKL`, `DF`, `VASC`
- **Class 1 (Malignant-Suspicious):** `MEL`, `BCC`, `AKIEC`

*Note: Raw dataset images and heavy model checkpoints are not included in the repository configuration to prevent excessively large clones.*

## Project Structure
```text
d:\CODING\OFFLINE-SKIN-CANCER-DETECTION
├── app/
├── data/
├── models/
├── reports/
└── src/
```

## Installation
Ensure you have Python installed. We highly recommend using a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Offline Application
From the root of the project directory, with the virtual environment activated, run:

```bash
streamlit run app/app.py
```

## Training and Evaluation
The repository includes the following scripts under `src/` to fully reproduce the dataset preparation, training, and evaluation steps locally:
- Data preparation: `src/create_binary_dataset.py`
- Split creation: `src/create_splits.py`
- Training: `src/train.py`
- Fine-tuning: `src/finetune.py`
- Evaluation: `src/evaluate.py`
- Model comparison: `src/compare_models.py`
- Threshold analysis: `src/threshold_analysis.py`
- Error analysis: `src/error_analysis.py`

## Evaluation Results
Results on the strictly held-out test set:

- **Accuracy:** 68.47%
- **Precision:** 39.53%
- **Recall/Sensitivity:** 90.88%
- **Specificity:** 62.41%
- **F1:** 55.10%
- **ROC-AUC:** 85.37%

*Confusion Matrix (Threshold 0.50):*
- True Negatives (TN): 734
- False Positives (FP): 442
- False Negatives (FN): 29
- True Positives (TP): 289

*(These values reflect dataset-specific statistical behavior and do not reflect clinical performance).*

## Error Analysis
At the current 0.50 threshold, the model produces 442 false positives and 29 false negatives. 
- `NV` + `BKL` account for approximately 97.3% of all false positives.
- `MEL` accounts for approximately 82.8% of all false negatives.

For deeper insights, please refer to the comprehensive error grids and reports located in the `reports/` directory.

## Limitations
- Evaluation is dataset-specific.
- No external-dataset validation was performed.
- No clinical validation was performed.
- The training and test sets contain severe class imbalance.
- Discrete metrics heavily rely on threshold dependence.
- Image variability profoundly affects model outputs.
- Model probabilities are completely statistical and do not imply medical certainty.

## Safety Disclaimer
**This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions.**
