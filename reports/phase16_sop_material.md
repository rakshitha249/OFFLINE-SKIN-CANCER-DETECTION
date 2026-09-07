# SOP Material

### Motivation
Developing SKIN VISION provided hands-on experience navigating the complexities of deep learning in computer vision. It highlighted my interest in building AI systems where interpreting model decisions is just as crucial as the accuracy metrics themselves.

### Technical challenge
The primary technical challenge involved managing a complex visual dataset (HAM10000). Implementing rigorous lesion-grouped data splits was essential to prevent data leakage—a critical step often overlooked in simplified tutorials. Fine-tuning an EfficientNet-B0 architecture required careful balance between learning new binary patterns and retaining pre-trained ImageNet features.

### Learning
- **Transfer learning:** Gained practical experience fine-tuning a modern CNN architecture to adapt to specialized biological imagery.
- **Evaluation:** Learned to prioritize threshold-independent metrics like ROC-AUC (85.37%) while understanding the trade-offs in Precision, Recall, and Specificity when applying a strict 0.50 decision threshold.
- **Class imbalance/error patterns:** Recognized the importance of error analysis over aggregate accuracy. Identifying that non-malignant classes like NV and BKL dominated false positives provided deep insight into the model's limitations.
- **Explainability:** Implemented Grad-CAM to visualize model attention, reinforcing the importance of transparency in AI outputs.
- **Deployment:** Transitioned from Jupyter notebooks to a structured Python project, building both a fully offline secure Streamlit application and a lightweight hosted demo.
- **Reproducibility:** Emphasized strict environment management and reproducible data pipelines.

### Research mindset
Rather than blindly optimizing for accuracy, I prioritized held-out evaluation and detailed error analysis. This approach ensured that the model's performance on the 1494-image test set was a realistic reflection of its capabilities on unseen data, revealing the nuanced challenges of false-positive patterns.

### Engineering mindset
The project evolved significantly from a raw model script into a robust software application. I engineered an offline-first architecture incorporating local PBKDF2-HMAC-SHA256 authentication, local prediction history logging, and real-time image-quality heuristics, demonstrating a holistic approach to building end-to-end machine learning products.

### Future work
Technically reasonable future directions include extending the pipeline to support the original seven-class multiclass formulation, implementing advanced class balancing techniques, exploring alternative backbone architectures (such as ConvNeXt), and conducting external validation on distinctly different datasets to test generalizability.
