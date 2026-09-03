# How I Built This Project

## 1. Problem Definition
**What was done:** I set out to build an end-to-end, locally runnable computer vision application capable of classifying skin lesion images.
**Why:** To create a complete AI research and educational prototype demonstrating data processing, deep learning model training, and interactive web application deployment without relying on cloud APIs.
**Output:** A clear project scope focused on building an offline Streamlit tool powered by PyTorch.

## 2. Dataset Preparation
**What was done:** I sourced the public HAM10000 dataset, containing over 10,000 images of skin lesions and a comprehensive metadata CSV.
**Why:** It is a well-documented benchmark dataset with sufficient volume for training deep convolutional neural networks.
**Output:** Raw image files and tabular metadata ready for processing.

## 3. Label Conversion
**What was done:** I mapped the dataset's 7 highly specific diagnostic classes into two broad groups: Malignant-Suspicious (MEL, BCC, AKIEC) and Non-malignant (NV, BKL, DF, VASC).
**Why:** To simplify the problem into a fundamental binary classification task, allowing for clear statistical metrics like ROC-AUC and threshold analysis.
**Output:** A processed CSV where every image was assigned a clean 0 or 1 binary label.

## 4. Data Splitting
**What was done:** I used scikit-learn's `GroupShuffleSplit` on the `lesion_id` feature to partition the data into 70% training, 15% validation, and 15% testing splits.
**Why:** Because multiple images in the dataset belong to the exact same physical lesion. A simple random split would leak images of the same lesion into both the training and test sets, artificially inflating performance.
**Output:** Three mutually exclusive CSV files ensuring strict data integrity, containing exactly 1,494 test images.

## 5. Preprocessing
**What was done:** I resized images to 224x224, applied basic augmentations during training (like rotations and flips), and normalized the pixel values to match ImageNet standards.
**Why:** 224x224 is the expected input size for the EfficientNet-B0 architecture, and augmentations help prevent overfitting by showing the model varied perspectives.
**Output:** PyTorch `Dataset` and `DataLoader` pipelines ready to feed tensors into the model.

## 6. Model Selection
**What was done:** I implemented an EfficientNet-B0 backbone using PyTorch's `torchvision` library and replaced its final layer with a single linear output neuron.
**Why:** EfficientNet-B0 offers an excellent trade-off between accuracy and computational efficiency, making it perfect for local, offline inference. The single neuron outputs a logit that maps easily to a binary probability.
**Output:** An untrained model architecture ready for PyTorch.

## 7. Initial Training
**What was done:** I trained the classification head using the AdamW optimizer (learning rate 0.0001), `BCEWithLogitsLoss`, and dynamically calculated weights to penalize the model heavily for missing the minority positive class.
**Why:** The dataset is heavily imbalanced. Without class weighting, the model would simply guess the majority class (Non-malignant) and achieve high accuracy while failing its primary task.
**Output:** A baseline model capable of basic feature recognition.

## 8. Fine-Tuning
**What was done:** I unfreezed layers deeper in the EfficientNet-B0 backbone and trained again with a significantly smaller learning rate (0.00001).
**Why:** To adapt the deep convolutional filters specifically to dermatological textures without destroying the foundational geometric features they learned from ImageNet.
**Output:** A highly specialized skin lesion feature extractor.

## 9. Validation
**What was done:** Throughout training, I evaluated the model against the 15% validation split after every epoch, tracking the ROC-AUC score.
**Why:** To monitor for overfitting and ensure I saved the checkpoint (`best_finetuned_model.pth`) that generalized best, rather than the one that just memorized the training set.
**Output:** The final selected model checkpoint.

## 10. Test Evaluation
**What was done:** I locked the model and ran inference exclusively on the 1,494-image held-out test set, capturing Accuracy, Recall, Precision, and ROC-AUC.
**Why:** To get an unbiased, mathematically sound estimate of the model's true statistical performance on unseen data.
**Output:** The final quantitative metrics (e.g., 85.37% ROC-AUC, 90.88% recall).

## 11. Error Analysis
**What was done:** I analyzed the confusion matrix at a 0.50 threshold and mapped the false positives and false negatives back to their original 7 diagnostic classes.
**Why:** To understand the model's blind spots. I discovered that over 97% of false positives were triggered by the NV and BKL categories.
**Output:** Extensive markdown reports documenting the exact structural weaknesses of the model.

## 12. Grad-CAM
**What was done:** I integrated the `pytorch-grad-cam` library to generate heatmaps over the analyzed images during inference.
**Why:** To provide visual explainability, proving whether the model was looking at the actual skin lesion or inappropriately focusing on background artifacts (like hair or rulers).
**Output:** A visual overlay capability.

## 13. Streamlit Application
**What was done:** I built a frontend using `streamlit` that allows users to upload images, runs the image through the PyTorch model, and displays the probability outputs cleanly.
**Why:** To convert abstract Python scripts and `.pth` files into an interactive, user-friendly software prototype.
**Output:** The `app.py` script and its resulting web interface.

## 14. Offline Inference
**What was done:** I ensured all dependencies, models, and processing logic executed locally on the host machine's CPU/GPU.
**Why:** To demonstrate privacy-first architecture and remove reliance on external cloud APIs or persistent internet connections during inference.
**Output:** A self-contained runtime environment.

## 15. Prediction History
**What was done:** I added logic to append every inference result to a local `history/prediction_history.csv` file, and built a UI table to display it.
**Why:** To give the application a sense of state and utility over multiple interactions.
**Output:** A functional, localized logging system.

## 16. Safety-Oriented Presentation
**What was done:** I audited the entire application UI and documentation to strip out words like "diagnosis", "safe", or "cancer detected," replacing them with "statistical model output" and "estimated probability".
**Why:** Because this is an educational prototype, not an FDA-approved medical device. It is ethically and technically imperative to frame AI outputs accurately.
**Output:** A highly professional, cautious, and accurate application UI.

## 17. Limitations
**What was done:** I documented the specific boundaries of the project, including the missing real-world clinical validation, the dataset bias, and the high false-positive rate.
**Why:** A mature engineering project acknowledges its boundaries and doesn't exaggerate its capabilities.
**Output:** A comprehensive Reproducibility and Limitations report concluding the project.
