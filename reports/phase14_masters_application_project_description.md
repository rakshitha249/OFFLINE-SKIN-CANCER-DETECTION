# Master's Application Material

## A. Short Description (2–3 Sentences)
Developed an offline, privacy-first computer vision pipeline using a fine-tuned EfficientNet-B0 to classify dermatoscopic images. The project emphasizes rigorous evaluation through lesion-grouped dataset splitting to prevent data leakage and incorporates explainable AI (Grad-CAM) within a fully local Streamlit application.

## B. Medium Paragraph
I engineered an end-to-end, offline machine learning pipeline for binary classification of skin lesions using a fine-tuned EfficientNet-B0 architecture. Prioritizing data integrity, I implemented lesion-grouped dataset splitting to prevent data leakage across the train/validation/test boundaries. The model achieved an ROC-AUC of 85.37% on a strictly held-out test set. To improve interpretability, I integrated Grad-CAM visualizations and image-quality heuristics into a local Streamlit application secured by offline PBKDF2-HMAC-SHA256 authentication, demonstrating a strong commitment to trustworthy AI and rigorous statistical evaluation.

## C. Detailed Academic Version
In this independent research prototype, I developed a comprehensive offline machine learning system to classify skin lesions using the HAM10000 dataset. To ensure robust statistical validity and prevent data leakage, I implemented a strict lesion-grouped data splitting strategy before fine-tuning an EfficientNet-B0 architecture. The model was evaluated exclusively on a held-out test set (N=1494), achieving an ROC-AUC of 85.37% and demonstrating high sensitivity (90.88%) alongside a thorough threshold and error analysis. To address the 'black-box' nature of deep learning, I integrated Gradient-weighted Class Activation Mapping (Grad-CAM) and programmatic image-quality heuristics. The entire pipeline was deployed as a fully offline Streamlit application with local session authentication, reflecting a strong emphasis on data privacy, explainable AI, and rigorous, reproducible machine learning engineering.

## D. Technical Skills Demonstrated
- **Deep Learning & Computer Vision:** PyTorch, EfficientNet-B0, Transfer Learning, Fine-Tuning.
- **Model Evaluation:** ROC-AUC analysis, Confusion Matrices, Precision-Recall trade-offs, Error Analysis.
- **Explainable AI (XAI):** Grad-CAM visualization.
- **Data Engineering:** Lesion-grouped dataset splitting (preventing data leakage), Data Augmentation, Pandas, NumPy.
- **Software Engineering:** Streamlit, Local PBKDF2 Authentication, Offline Inference, Git Version Control.

## E. Relevant Research Interest Areas
- Computer Vision and Image Classification
- Trustworthy and Explainable AI (XAI)
- Machine Learning Systems and Deployment
- Rigorous Model Evaluation and Error Analysis
- Privacy-Preserving Offline AI Applications
