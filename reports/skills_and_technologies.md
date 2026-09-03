# Skills and Technologies Demonstrated

This table maps the specific technologies and concepts utilized within the Offline Skin Lesion Analyzer project to the exact implementations in the repository.

| Technology / Concept | Where Used | What I Demonstrated |
|---|---|---|
| **Python** | Entire Codebase | Structured, modular script development, virtual environment management, and object-oriented programming. |
| **PyTorch** | `model.py`, `train.py`, `evaluate.py`, `app.py` | Building CNN architectures, managing tensors, configuring custom training loops, and executing inference. |
| **torchvision** | `dataset.py`, `model.py` | Instantiating pre-trained EfficientNet-B0 architectures and composing image transformations (resize, normalize, ToTensor). |
| **EfficientNet-B0** | `model.py` | Adapting a state-of-the-art, highly parameter-efficient CNN backbone for a specific visual classification task. |
| **Pandas** | `create_splits.py`, `evaluate.py`, `app.py` | Parsing dataset metadata, managing data splits, calculating summary statistics, and writing/reading local prediction history CSVs. |
| **NumPy** | `app.py`, `evaluate.py` | Manipulating image arrays for heuristic image-quality checks (variance, brightness) and handling prediction arrays. |
| **Pillow (PIL)** | `dataset.py`, `app.py` | Loading raw image files, resizing, and converting formats before tensor transformation. |
| **scikit-learn** | `create_splits.py`, `evaluate.py` | Executing strict `GroupShuffleSplit` for data leakage prevention, and calculating ROC-AUC, F1, Precision, and Recall metrics. |
| **Matplotlib** | `plot_training_history.py`, `plot_error_analysis.py` | Generating ROC curve plots and visual confusion matrices for quantitative reporting. |
| **Streamlit** | `app.py` | Developing a responsive, interactive web application frontend directly from Python to serve the PyTorch model. |
| **Grad-CAM** | `app.py`, `gradcam_test.py` | Implementing gradient-based explainability visual overlays to highlight feature importance in model decisions. |
| **Transfer Learning** | `train.py`, `finetune.py` | Replacing the classifier head of an ImageNet-trained model and selectively unfreezing deeper layers for domain adaptation. |
| **Binary Classification** | `model.py`, `evaluate.py` | Configuring a single-neuron output, `BCEWithLogitsLoss`, and sigmoid activations for 0-to-1 probability mapping. |
| **Model Evaluation** | `evaluate.py`, `reports/` | Conducting rigorous threshold analyses and evaluating error distribution (FP/FN) across original diagnostic categories. |
| **Git / GitHub** | `.gitignore`, `README.md` | Structuring a clean repository, excluding large binary assets, and writing comprehensive markdown documentation. |
