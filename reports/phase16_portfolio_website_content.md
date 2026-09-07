# Portfolio Website Content

### Project title
SKIN VISION — Offline Skin Lesion Analyzer

### One-line tagline
An AI research prototype for binary skin-lesion classification utilizing EfficientNet-B0 and Grad-CAM explainability.

### Overview
SKIN VISION is an end-to-end machine learning project exploring the binary classification of skin lesions. Built as an educational prototype, it leverages the HAM10000 dataset to train a deep learning model that estimates probabilities for Non-malignant vs. Malignant-Suspicious patterns. The project prioritizes responsible AI practices, utilizing strict held-out evaluation, extensive error analysis, and visual explainability over medical diagnostic claims. 

### Problem
Applying computer vision to complex biological datasets requires rigorous methodology to prevent data leakage and ensure reliable evaluation. Furthermore, deep learning models often act as "black boxes," making it difficult to understand why a specific prediction was made, which is critical when analyzing sensitive imagery.

### Approach
I formulated a binary classification task and fine-tuned an EfficientNet-B0 model using PyTorch. To prevent data leakage, I implemented lesion-grouped data splitting. The model was evaluated on a strictly held-out test set, and Grad-CAM was integrated to provide spatial visualization of the model's decision-making process. The entire pipeline was packaged into a local Streamlit application.

### Technologies
Python, PyTorch, EfficientNet-B0, Streamlit, OpenCV, Grad-CAM, Pandas, NumPy.

### Key features
- Fine-tuned EfficientNet-B0 binary classifier.
- Local Streamlit application with PBKDF2-HMAC-SHA256 authentication.
- Grad-CAM visualizations to highlight model attention.
- Programmatic image-quality analysis heuristics.
- Continuous model probabilities and threshold-distance interpretation.

### Results
On a held-out test set of 1494 images, the model achieved a ROC-AUC of 85.37% and an accuracy of 68.47%. Error analysis revealed that false positives were primarily driven by non-malignant NV and BKL lesions, demonstrating the complexities of the binary grouping.

### Explainability
Grad-CAM was implemented to generate heatmaps directly in the UI, allowing users to inspect which regions of the input image most strongly influenced the final prediction, promoting transparency.

### Deployment
The project supports two deployment modes: a fully offline/local inference application emphasizing data privacy, and a lightweight public hosted demonstration that dynamically retrieves the model checkpoint from a GitHub Release.

### Limitations
This project is explicitly a technical and educational prototype. It performs binary rather than multiclass classification and is restricted to the specific characteristics of the HAM10000 dataset. It is not clinically validated and possesses no medical diagnostic capabilities.

### Links
- **GitHub Repository:** [ADD VERIFIED GITHUB URL]
- **Live Demo:** [ADD VERIFIED STREAMLIT URL]
