# Statement of Purpose (SOP) Material

*This document provides truthful, technically accurate material based directly on the Offline Skin Lesion Analyzer project. Adapt these paragraphs into your own voice for your Master's Statement of Purpose.*

## 1. Project Introduction
During my independent research, I developed the Offline Skin Lesion Analyzer, an end-to-end machine learning pipeline that classifies dermatoscopic images. The project demonstrates a complete lifecycle from data engineering to model deployment, utilizing a fine-tuned EfficientNet-B0 architecture packaged within an offline, privacy-preserving application.

## 2. Technical Motivation
I was highly motivated by the challenge of bridging deep learning with strict data privacy. I chose to build an entirely offline system to explore how complex computer vision models could run locally on consumer hardware without exposing sensitive image data to cloud APIs. Furthermore, I wanted to rigorously address the 'black-box' nature of deep learning through explainability techniques.

## 3. What Was Built
I engineered a fully offline Streamlit application that integrates a PyTorch-based binary classifier, Grad-CAM visual explainability, and basic image-quality heuristics. The system includes local PBKDF2-HMAC-SHA256 authentication and local prediction logging, creating a secure, self-contained environment for running model inference.

## 4. Dataset / Preprocessing
The model leverages the HAM10000 dataset, mapped to a binary classification problem. A critical step in my pipeline was addressing potential data leakage. I implemented a strict lesion-grouped data splitting strategy—grouping by `lesion_id`—to guarantee that multiple images of the exact same physical lesion did not mistakenly cross into both the training and test sets.

## 5. Model Selection
I selected EfficientNet-B0 as the core architecture. This choice provided an optimal balance between parameter efficiency and representation capability, allowing the model to perform highly effective feature extraction while remaining lightweight enough for rapid offline inference without a dedicated GPU.

## 6. Training / Fine-tuning
Starting with ImageNet pre-trained weights, I implemented a transfer learning strategy. After an initial phase of training the final linear layer, I systematically unfroze specific convolutional blocks to fine-tune the feature representations to dermatoscopic images. Validation loss and ROC-AUC metrics were monitored closely across epochs to select the best checkpoint.

## 7. Evaluation
The model was evaluated exclusively on a held-out test set (1,494 images), achieving an ROC-AUC of 85.37%. Rather than relying solely on a single threshold, I conducted a comprehensive threshold analysis, demonstrating the trade-offs between precision and recall, ultimately configuring the prototype at a 0.50 threshold that yielded a 90.88% sensitivity.

## 8. Error Analysis
I conducted a deep error analysis to understand the model's limitations. By mapping errors back to their original subclasses, I discovered that the vast majority of false positives originated from non-malignant nevi (NV) and benign keratosis (BKL). This analysis proved invaluable for understanding exactly where the model struggles with complex biological variance.

## 9. Explainability
To increase interpretability, I integrated Gradient-weighted Class Activation Mapping (Grad-CAM) into the pipeline. By visualizing the spatial regions that most influenced the model's prediction, I created a tool to inspect the model's reasoning, reinforcing the difference between a raw probability score and true diagnostic understanding.

## 10. Engineering Challenges
A significant engineering challenge was deploying the PyTorch model seamlessly into a responsive, fully local Streamlit application. I had to ensure that the heavy tensor operations for inference and Grad-CAM generation were optimized enough to run without perceptible UI freezing, while concurrently handling session state and local authentication securely.

## 11. Learning Outcomes
This project cemented my understanding of the complete machine learning lifecycle. I learned the critical importance of rigorous data splitting (avoiding leakage), the trade-offs inherent in threshold selection, the nuances of fine-tuning pre-trained networks, and the necessity of thoroughly documenting model limitations and false-positive burdens.

## 12. Connection to AI/ML Interests
Building this system deepened my interest in Trustworthy AI and Machine Learning Systems. It highlighted the gap between raw statistical accuracy and actual interpretability. My experience with Grad-CAM and error analysis has driven my passion to explore more robust, transparent, and fair machine learning models.

## 13. Connection to Master's Study
I want to pursue a Master's degree to move beyond building prototypes and to formally study advanced machine learning architectures, statistical learning theory, and explainable AI methodologies. The challenges I encountered with class imbalance and threshold dependence in this project are exact areas I wish to research rigorously under academic mentorship.

## 14. Future Work
In the future, I aim to expand this work by addressing the severe class imbalances via advanced sampling or loss weighting, exploring multiclass classification without losing the rigor of the current binary evaluation, and researching more mathematically robust methods for probability calibration.
