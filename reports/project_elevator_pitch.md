# Project Elevator Pitch

## 30-Second Version
"I built an offline AI educational prototype that classifies skin lesion images using Python and PyTorch. I took a public dataset of over 10,000 images, carefully split them to prevent data leakage, and fine-tuned an EfficientNet-B0 deep learning model. Then, I wrapped the trained model in a local Streamlit web app that provides statistical predictions, heuristic image quality checks, and visual explainability using Grad-CAM, all running entirely offline on the user's machine."

## 60-Second Version
"I developed an offline computer vision prototype focused on binary skin lesion classification. The problem was building a robust, fully localized pipeline without relying on cloud APIs. I used the HAM10000 dataset, mapping its seven classes into a binary structure, and implemented strict lesion-level data splitting to ensure evaluation integrity. I trained and fine-tuned an EfficientNet-B0 model in PyTorch, which achieved an 85.37% ROC-AUC on the held-out test set. 

To make the model interactive, I built a Streamlit application that runs 100% locally. It accepts an image, evaluates its quality, runs inference, and generates a Grad-CAM heatmap to explain which regions influenced the model's statistical output. A key limitation I documented is that while it achieves high recall, it produces a high rate of false positives on specific benign lesion types, reinforcing that this is purely a statistical research tool and not a clinical diagnostic device."

## 2-Minute Technical Version
"This project is a complete end-to-end machine learning pipeline built to explore offline computer vision classification.

I started with the HAM10000 dataset, preprocessing the metadata to map seven diagnostic categories into a binary Malignant-Suspicious versus Non-malignant schema. To prevent data leakage—since multiple images can belong to the same physical lesion—I used scikit-learn's `GroupShuffleSplit` on the `lesion_id` feature to create strict 70/15/15 train, validation, and test splits.

For the model, I initialized an EfficientNet-B0 architecture in PyTorch. I replaced the classifier head for binary output and trained it using AdamW, a dynamic positive-class weight to handle imbalance, and `BCEWithLogitsLoss`. After initial training, I selectively unfreezed backbone layers and fine-tuned at a lower learning rate, using validation ROC-AUC to select the optimal checkpoint.

I evaluated the final model on the 1,494-sample held-out test set, achieving 85.37% ROC-AUC, 68.47% accuracy, and 90.88% recall at a 0.50 threshold. I also conducted an in-depth threshold and error analysis, discovering that over 97% of false positives were concentrated in the NV and BKL source classes.

Finally, I built a local Streamlit inference application. The app performs offline inference, logs predictions to a local CSV, assesses basic image quality metrics like sharpness and brightness, and utilizes the `pytorch-grad-cam` library to generate explainability heatmaps. The entire UI is heavily framed around safety, explicitly communicating the model output strength based on threshold distance, and clearly disclaiming that the probabilities are purely statistical research outputs, not medical diagnoses."
