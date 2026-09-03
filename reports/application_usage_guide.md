# Application Usage Guide

## 1. Overview

The Offline Skin Lesion Analyzer is a Streamlit web application that accepts an uploaded image of a skin lesion and provides a model-based binary classification. It is an offline AI research and educational prototype. It is **not** a medical diagnostic application and should not be used to make clinical decisions.

---

## 2. Prerequisites

To run this application locally, you must satisfy the following requirements:
- Python 3.9+ (Highly recommended to use a virtual environment).
- Required Python packages: `streamlit`, `torch`, `torchvision`, `pillow`, `numpy`, `pandas`, `pytorch-grad-cam`. (These are listed in `requirements.txt`).
- The trained model checkpoint (see **Required Local Model** section).

*Note: A GPU is optional. The application will automatically use CUDA if available, otherwise it falls back to the CPU.*

---

## 3. Repository Setup

Use the following commands to configure the local repository on your system:

```bash
git clone https://github.com/rakshitha249/OFFLINE-SKIN-CANCER-DETECTION.git
cd OFFLINE-SKIN-CANCER-DETECTION

python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 4. Required Local Model

To keep the repository size manageable and comply with hosting limits, the trained PyTorch checkpoint is intentionally excluded from Git tracking. A fresh clone cannot immediately run inference without it.

The application strictly expects the trained model checkpoint to be available at this local path:
`models/best_finetuned_model.pth`

You must obtain or reproduce this checkpoint separately and place it in the `models/` directory before starting the application.

---

## 5. Launching the Application

With your virtual environment activated and the model checkpoint in place, start the application by running:

```bash
streamlit run app/app.py
```

Streamlit will start a local server and typically open your default web browser automatically to the local network URL serving the interface.

---

## 6. Uploading an Image

To upload an image for analysis:
1. Open the application in your browser.
2. Under the **Upload Image** section, click "Browse files" or drag and drop an image.
3. Supported formats are: `jpg`, `jpeg`, and `png`.
4. Click the **Analyze Image** button.
5. Wait for the local inference to complete.
6. Review the displayed model output.

---

## 7. Model Prediction Section

After analysis, the application generates a hierarchy of statistical outputs:

- **Model prediction:** "Malignant-Suspicious" or "Non-malignant".
- **Estimated model probability:** The raw statistical output for both classes.
- **Malignant-Suspicious probability & Non-malignant probability:** Displayed as percentages totaling 100%.
- **Decision threshold:** The application uses **0.50** as its decision boundary.
- **Distance from threshold:** A calculated percentage margin from the 0.50 boundary.
- **Model output strength:** An interpretation based on the threshold distance.

These values are statistical model outputs, not measures of medical certainty. The 0.50 decision threshold is an application decision boundary, not a clinically optimized threshold.

---

## 8. Understanding Threshold Distance

The application contextualizes how sensitive the prediction is to small mathematical changes in the model output probability:

- **Near-threshold model output:** The model probability is very close to the decision threshold (< 0.10 margin).
- **Moderate distance from threshold:** The model probability is neither very close to nor far from the current decision threshold (< 0.25 margin).
- **Model output is farther from the decision threshold:** The model probability is farther from the current classification threshold.

*Note: These interpretations describe mathematical threshold proximity, not medical risk.*

---

## 9. Image Quality Section

The application assesses three basic image characteristics prior to the model output:
- **Resolution:** Checks image pixel dimensions.
- **Brightness:** Checks mean grayscale pixel intensity.
- **Sharpness:** Checks variance of pixel differences.

An image-quality warning does not prevent inference. The model prediction will still be generated, but the application warns if image characteristics fall outside preferred ranges. This quality check is separate from the model prediction and does not validate the model's accuracy.

---

## 10. Grad-CAM Section

When an image is analyzed, the application generates a Grad-CAM overlay alongside the original uploaded image. 

Grad-CAM describes regions that contributed more strongly to the model output. It is an explainability visualization and is not a medical diagnostic map. It simply provides a visual explanation of the model behavior.

---

## 11. Prediction History

The application records model outputs during usage and displays them in the **Prediction History** section at the bottom of the page.

The data is stored locally in the file:
`history/prediction_history.csv`

The CSV schema records:
`timestamp`, `image_name`, `prediction`, `malignant_probability`, `non_malignant_probability`, `confidence`, and `image_quality`.

*Note: These entries are merely a log of application usage and model outputs. They do not represent a patient or medical record.*

---

## 12. Empty States and Error Handling

- **Model checkpoint is missing:** The application displays an error reading: *"Model checkpoint is missing. The application cannot perform predictions until the trained model is supplied at 'models/best_finetuned_model.pth'. This is a local/offline application."* It will safely stop execution until the model is provided.
- **No prediction history exists:** The history section displays: *"No prediction history is available yet."*
- **Grad-CAM fails:** If the overlay fails to generate, the application safely continues showing the model output and displays a warning: *"Grad-CAM visualization could not be generated for this image."*
- **Invalid image:** If an uploaded image is corrupted, it displays: *"Error processing the uploaded image. Please ensure it is a valid image file. Details: [error message]"*

---

## 13. Offline Operation

The application performs inference entirely locally. 
The workflow utilizes your local image, local Python environment, local model checkpoint, local hardware computation, and the local history CSV. Inference does not depend on an external inference API or cloud model.

---

## 14. Troubleshooting

| Problem | Likely Cause | Solution |
|---|---|---|
| **Application will not start** | Environment/dependency issue | Verify the virtual environment is activated and requirements are installed. |
| **Model missing error** | Checkpoint not present | Place the separately obtained checkpoint at the expected local path: `models/best_finetuned_model.pth`. |
| **Image cannot be processed** | Invalid/unsupported image | Ensure the uploaded image is a valid `jpg`, `jpeg`, or `png` format. |
| **History is empty** | No outputs recorded yet | Upload and run an inference on at least one image. |
| **Grad-CAM unavailable** | Explainability computation failed | Review the application warning; the model prediction may still be successfully available above. |

---

## 15. Quick Start (Beginner Workflow)

1. Clone repository (`git clone https://github.com/rakshitha249/OFFLINE-SKIN-CANCER-DETECTION.git`)
2. Create and activate a virtual environment.
3. Install requirements (`pip install -r requirements.txt`).
4. Obtain the trained checkpoint separately.
5. Place the checkpoint at `models/best_finetuned_model.pth`.
6. Run Streamlit (`streamlit run app/app.py`).
7. Upload an image (`jpg`/`jpeg`/`png`).
8. Review the Image Quality assessment.
9. Click "Analyze Image".
10. Review the statistical Model Output and Grad-CAM visualization.
11. Check the local Prediction History log at the bottom.

---

## 16. Safety and Limitations

> **This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions.**

- Model outputs are **not** medical diagnoses.
- The test results for this model do not establish clinical validity.
- The application should not be used for clinical decision-making.

---

## 17. Related Documentation

- [Project README](../README.md)
- [System Architecture](architecture.md)
- [Dataset and Methodology](dataset_and_methodology.md)
- [Results and Evaluation](results_and_evaluation.md)
- [Consolidated Evaluation Report](consolidated_evaluation_report.md)
