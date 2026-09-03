# Offline Skin Cancer Detection

This project is an AI research and educational prototype for offline image-based binary classification of skin lesions.

> [!WARNING]
> **Safety Disclaimer:** This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions.

---

## Overview

The Offline Skin Cancer Detection project demonstrates an end-to-end machine learning pipeline, from dataset preparation to offline inference. It provides a local web application where users can upload an image of a skin lesion and receive a model-based classification.

The application operates completely offline and prioritizes interpretability by providing an estimated model probability, heuristic image-quality assessment, and Grad-CAM explainability visualizations to describe model behavior.

---

## Key Features

- **Offline image inference:** All processing is conducted locally without cloud dependencies.
- **EfficientNet-B0 binary classification:** Utilizes a fine-tuned EfficientNet-B0 model.
- **Estimated model probability:** Provides probabilistic scores alongside a strict 0.50 decision threshold.
- **Threshold-distance/model-output-strength information:** Contextualizes the classification sensitivity based on threshold proximity.
- **Image-quality assessment:** Programmatic evaluation of image resolution, brightness, and sharpness.
- **Grad-CAM explainability visualization:** Highlights image regions contributing more strongly to the model output.
- **Local prediction history:** Logs application usage and model outputs to a local CSV file.
- **Graceful missing-model/error handling:** Robust UI handling for missing PyTorch checkpoints and corrupted image inputs.

---

## Technology Stack

- **Python** 
- **PyTorch / torchvision** (Model architecture and training)
- **EfficientNet-B0** (Base model architecture)
- **Streamlit** (Local web application interface)
- **NumPy** & **Pandas** (Data manipulation and history tracking)
- **Pillow** (Image loading and processing)
- **pytorch-grad-cam** (Explainability visualizations)
- **scikit-learn** (Metrics and data splitting)
- **Matplotlib** (Evaluation artifact generation)

---

## Dataset

This project utilizes the publicly available HAM10000 / ISIC dataset. 

The original dataset features seven diagnostic classes:
`NV`, `BKL`, `MEL`, `BCC`, `AKIEC`, `VASC`, `DF`

For this research prototype, the classes are mapped into a binary schema:

### Non-malignant
- `NV`
- `BKL`
- `DF`
- `VASC`

### Malignant-Suspicious
- `MEL`
- `BCC`
- `AKIEC`

*Note: This binary mapping enables the model to output a single statistical probability for research and educational analysis. It does not establish clinical severities.*

---

## Dataset Splitting

To evaluate the model rigorously, the dataset is split using `GroupShuffleSplit` grouping by `lesion_id`. Grouping ensures that multiple images of the exact same physical lesion remain exclusively within the same dataset split, strictly preventing data leakage.

The approximate split sizes are:
- **Training:** ~70%
- **Validation:** ~15%
- **Test:** ~15% (Exactly 1494 images held out exclusively for final evaluation)

---

## Methodology

The pipeline follows these high-level steps:
1. Dataset preparation and binary label mapping.
2. Lesion-grouped splitting to prevent data leakage.
3. Training augmentations applied to balance class representations.
4. EfficientNet-B0 initialization and fine-tuning.
5. Model validation and best checkpoint selection.
6. Held-out test evaluation.

See [Dataset and Methodology](reports/dataset_and_methodology.md) for the detailed dataset preparation, splitting, preprocessing, training, and evaluation methodology.
See [System Architecture](reports/architecture.md) for the complete training and inference pipeline.

---

## Model

- **Architecture:** The project uses an EfficientNet-B0 backbone.
- **Classification Head:** The final layers are adapted for a binary classification task.
- **Output:** The model produces a single binary logit, which a Sigmoid function converts into an estimated model probability between 0 and 1.
- **Threshold:** A 0.50 decision threshold determines the final classification.

The model produces a statistical output that is converted to an estimated model probability. This output is not a measure of medical certainty, and the 0.50 threshold is not a clinically optimized boundary.

---

## Evaluation Results

These results describe the model's statistical performance on the held-out test set (1494 images) and do not represent clinical validation.

| Metric | Result |
|---|---:|
| Accuracy | 68.47% |
| Precision | 39.53% |
| Recall / Sensitivity | 90.88% |
| Specificity | 62.41% |
| F1 Score | 55.10% |
| ROC-AUC | 85.37% |

The fine-tuned model achieved an ROC-AUC of 85.37%. At the 0.50 application threshold, it demonstrated high recall (90.88%) alongside lower precision due to a substantial number of false positive predictions. 

See [Results and Evaluation](reports/results_and_evaluation.md) for detailed metrics, confusion matrix analysis, and baseline comparisons.

---

## Error Analysis

A comprehensive error analysis was conducted on the held-out test set predictions at the 0.50 threshold:
- False positives were dominated by `NV` and `BKL`.
- `NV` and `BKL` together accounted for approximately 97.3% of all false positives.
- False negatives were dominated by `MEL`.
- `MEL` accounted for approximately 82.8% of all false negatives.
- Errors occurred both near and farther from the 0.50 threshold, indicating complex visual overlaps in the dataset.

For detailed analysis grids and insights, see [Error Analysis Report](reports/error_analysis_report.md).

---

## Application

The project provides a Streamlit application (`app/app.py`) for offline inference.

### Model Prediction
The application displays the model prediction, the estimated model probability (for both classes), and the 0.50 decision threshold context. It calculates the mathematical distance from the threshold to indicate the model output strength.

### Image Quality
Programmatic evaluation of resolution, brightness, and sharpness. These are presented as image characteristics to provide heuristic feedback regarding the quality of the uploaded file.

### Grad-CAM
Grad-CAM provides an explainability visualization showing image regions that contributed more strongly to the model output. Grad-CAM describes model behavior and is not a medical diagnostic map.

### Prediction History
Model outputs are stored locally in a CSV file at `history/prediction_history.csv`. 
The schema includes: `timestamp`, `image_name`, `prediction`, `malignant_probability`, `non_malignant_probability`, `confidence`, and `image_quality`. 
This is a session log, not a patient or medical record.

---

## System Architecture

See [System Architecture](reports/architecture.md) for the complete training and inference pipeline, including flow diagrams of the dataset handling and Streamlit UI.

---

## Project Structure

```text
OFFLINE-SKIN-CANCER-DETECTION/
│
├── app/
│   └── app.py                        # Streamlit web application
│
├── src/
│   ├── analyze_dataset.py            # Dataset exploration and statistics
│   ├── compare_models.py             # Script to compare baseline vs fine-tuned
│   ├── create_binary_dataset.py      # Script mapping HAM10000 to binary labels
│   ├── create_error_grids.py         # Script to generate visual error analysis grids
│   ├── create_splits.py              # Lesion-grouped Train/Val/Test splitting
│   ├── dataset.py                    # PyTorch Dataset definitions
│   ├── error_analysis.py             # Script to generate error analysis CSVs
│   ├── evaluate.py                   # Held-out test set evaluation script
│   ├── finetune.py                   # Model fine-tuning script
│   ├── model.py                      # EfficientNet-B0 architecture setup
│   ├── threshold_analysis.py         # Script analyzing metrics across thresholds
│   └── train.py                      # Initial model training script
│
├── data/
│   ├── raw/                          # Directory for downloaded HAM10000 images/metadata
│   └── processed/                    # Directory for generated CSV splits
│
├── models/                           # Directory for saved PyTorch checkpoints (.pth)
│
├── history/
│   └── prediction_history.csv        # Local log of application predictions
│
├── reports/                          # Generated markdown reports, CSVs, and PNG charts
│
├── requirements.txt                  # Python package dependencies
├── .gitignore                        # Git exclusion rules
└── README.md                         # Project documentation
```

---

## Visual Demo

A complete set of application interface documentation is available in the [Visual Portfolio Guide](reports/portfolio_visuals.md). 

*(Note: Screenshots are pending manual capture to guarantee authenticity and avoid automated mock-ups).*

---

## Installation

Ensure you have Python installed (version 3.9+ recommended). 

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rakshitha249/OFFLINE-SKIN-CANCER-DETECTION.git
   cd OFFLINE-SKIN-CANCER-DETECTION
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Reproducibility and Limitations

**Important Note for Fresh Clones:**
To keep the repository footprint small and comply with hosting limits, raw datasets, processed split files, and `.pth` model checkpoints are intentionally excluded from version control (`.gitignore`).

Therefore, a fresh clone **does not immediately contain the dataset or trained checkpoint required for local inference**. 

You must either:
1. Obtain the HAM10000 dataset, place it in `data/raw/`, and reproduce the training process using the scripts provided in `src/`.
2. Provide the trained checkpoint (`best_finetuned_model.pth`) manually and place it in the `models/` directory.

Please see the comprehensive [Reproducibility and Limitations](reports/reproducibility_and_limitations.md) report for detailed documentation on fresh clone requirements, dataset specifics, training workflows, test-set constraints, and performance limitations.

## Why This Project

This repository demonstrates the execution of a complete, end-to-end machine learning computer vision pipeline. Key technical highlights include:
- **Strict Data Splitting:** Utilizing `GroupShuffleSplit` on physical lesion IDs to prevent data leakage.
- **Transfer Learning:** Custom fine-tuning of an EfficientNet-B0 backbone using PyTorch and dynamic class-weighting.
- **Quantitative Evaluation:** Detailed ROC-AUC, threshold, and confusion matrix analysis on a rigorously held-out test set.
- **Explainability:** Integration of Grad-CAM to visualize statistical model feature prioritization.
- **Offline Application:** A fully localized Streamlit web application providing inference and heuristic image-quality assessments without cloud dependencies.
- **Safety and Reproducibility:** Careful documentation of model limitations, false-positive constraints, and avoidance of unsupported clinical claims.

## For Recruiters / Reviewers

To quickly evaluate the technical depth of this project, please refer to the following generated reports:
- **[System Architecture](reports/architecture.md)**
- **[Dataset and Methodology](reports/dataset_and_methodology.md)**
- **[Results and Evaluation](reports/results_and_evaluation.md)**
- **[Application Usage Guide](reports/application_usage_guide.md)**
- **[Reproducibility and Limitations](reports/reproducibility_and_limitations.md)**
- **[Visual Portfolio Guide](reports/portfolio_visuals.md)**
- **[Skills and Technologies Demonstrated](reports/skills_and_technologies.md)**

---

## Application Usage

The offline Streamlit application allows users to upload local skin lesion images for model-based binary classification. 

To launch the application locally (once the environment is configured and the trained checkpoint is placed at `models/best_finetuned_model.pth`), run:

```bash
streamlit run app/app.py
```

See the [Application Usage Guide](reports/application_usage_guide.md) for detailed instructions on uploading images, understanding model output strength, interpreting Grad-CAM, and troubleshooting errors.

---

## Training and Evaluation

If you wish to reproduce the project's training and evaluation, the `src/` directory contains all necessary scripts. 

You must first download the HAM10000 dataset metadata and images into `data/raw/`. Then, execute the scripts sequentially (e.g., `create_binary_dataset.py` -> `create_splits.py` -> `train.py` -> `finetune.py` -> `evaluate.py`). Detailed evaluation artifacts and visual plots will be generated in the `reports/` directory.

---

## Limitations and Safety

- **Research/educational prototype:** This project is designed for educational exploration of deep learning.
- **Not a medical diagnostic device:** The system cannot and should not be used for clinical decision-making.
- **Statistical outputs:** Model probabilities are statistical outputs representing mathematical patterns, not medical certainty.
- **No clinical validity:** Performance on the held-out test set does not establish clinical validity or safety.
- **Dataset limitations:** The model inherits all biases and limitations of the original HAM10000 dataset, and there is no claim of generalization to real-world clinical settings.
- **Threshold context:** The 0.50 threshold is an application-level decision boundary for binary mapping, not a clinically optimized threshold.

> [!WARNING]
> This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions.
