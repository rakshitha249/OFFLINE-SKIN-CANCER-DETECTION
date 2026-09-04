# Phase 13.7 — Installation & Reproducibility

## 1. Overview
The Offline Skin Lesion Analyzer is engineered for localized execution. To ensure privacy and avoid version control bloat, heavy artifacts (datasets, models) and private local states (environments, authentication) are actively excluded from the GitHub repository. Consequently, a fresh clone requires local environment configuration and independent acquisition of specific ML artifacts before inference can occur.

## 2. Prerequisites
- **Operating System**: Compatible with Windows, macOS, or Linux (Windows documented as primary).
- **Python**: A modern Python 3.x environment (exact version is not strictly pinned by the repository, but typically Python 3.9+ is recommended for PyTorch/Streamlit compatibility).
- **Git**: Required to clone the repository framework.

## 3. Repository Setup
Begin by cloning the repository structure to your local machine:
```bash
git clone https://github.com/rakshitha249/OFFLINE-SKIN-CANCER-DETECTION.git
cd OFFLINE-SKIN-CANCER-DETECTION
```
*Note: A fresh clone pulls the application source code, evaluation reports, and training scripts. It does **not** include the raw datasets or the trained model checkpoint.*

## 4. Virtual Environment
Isolate project dependencies by establishing a virtual environment:

**Windows (Git Bash):**
```bash
python -m venv .venv
source .venv/Scripts/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 5. Dependencies
With the virtual environment active, install the strictly pinned requirements:
```bash
pip install -r requirements.txt
```

**Dependency Audit:**

| Package | Purpose | Used By |
|---|---|---|
| `torch` | Core deep learning framework | Model inference, training, tensor ops |
| `torchvision` | Computer vision utilities | Image preprocessing, EfficientNet backbone |
| `opencv-python` | Image processing | Image quality heuristics (Sharpness/Blur) |
| `Pillow` | Image loading | UI upload handling, basic image transforms |
| `numpy` | Numerical operations | Array manipulation, metrics calculations |
| `pandas` | Data manipulation | Dataset metadata reading, history CSV logging |
| `scikit-learn` | Machine learning metrics | Train/Test splits, ROC-AUC calculation |
| `matplotlib` | Visualization | Plotting ROC curves, history graphs |
| `streamlit` | Application framework | Complete frontend UI and backend web server |
| `grad-cam` | Explainability | Generating visual heatmap overlays |

## 6. Dataset Setup
If you intend to reproduce the training process or run the authoritative test evaluations, you must acquire the dataset:
- **Dataset**: HAM10000 / ISIC dataset.
- **Placement**: Raw dataset images and the authoritative metadata CSV must be placed manually into the `data/raw/` directory.
- **Action**: Run the `src/create_splits.py` scripts to generate the lesion-grouped `data/processed/` partitions.
*(Note: These files are excluded from Git due to licensing and size constraints).*

## 7. Model Checkpoint Setup
**Crucial for Inference:** The Streamlit application relies on a fine-tuned model checkpoint which is excluded from Git (typically `models/best_finetuned_model.pth`). 
A fresh clone cannot perform inference until this checkpoint is available. Users must either:
1. Complete the dataset setup and execute the training/fine-tuning scripts to generate the checkpoint locally.
2. Obtain the specific `.pth` file from the project author and place it in the `models/` directory.

## 8. Authentication Setup
The application features local authentication. 
- On the first application run, if `auth/users.json` is missing or empty, the application intercepts the user and presents a first-user setup screen.
- The user configures a local username and password.
- The application then securely logs the user into the local session.
- Authentication relies strictly on local JSON storage and does not interface with cloud providers.

## 9. Running the Application
Once the dependencies are installed and the `models/best_finetuned_model.pth` checkpoint is in place, launch the Streamlit server:

```bash
python -m streamlit run app/app.py
```
*(Windows direct executable alternative: `./.venv/Scripts/python.exe -m streamlit run app/app.py`)*

Access the local UI in a web browser at: `http://localhost:8501`

## 10. Offline Inference
"Offline" in the context of this project means that the active application workload executes completely independently of the internet. Once the prerequisites (packages, dataset, checkpoint) are situated on the host machine:
- Image processing is local.
- PyTorch model loading and inference are local.
- Authentication validation is local.
- Prediction history logging is local.

## 11. Evaluation Reproduction
- **Evaluation reproducibility**: The logic to evaluate the model is highly reproducible. The evaluation scripts (`src/evaluate.py`), threshold analyses, and error analyses are preserved. However, executing them requires the user to locally reconstruct the dataset and the model checkpoint as detailed above.

## 12. Training Reproduction
- **Training reproducibility**: The repository includes the complete suite of source scripts, split logic (`create_splits.py`), and pinned requirements necessary to train the model from scratch. The hyperparameters and architecture are preserved in the code. Because the raw dataset is not included, bit-for-bit exact reproduction of the `.pth` file depends heavily on identical dataset acquisition and non-deterministic GPU/CPU training variances.

## 13. Git-Excluded Artifacts
The following artifacts have distinct Git exclusion rules impacting a fresh clone:

| Artifact | Git status | Reason |
|---|---|---|
| Raw dataset | Excluded | Large dataset size / third-party licensing. |
| Processed data | Excluded | Locally generated artifacts derived from raw data. |
| Model checkpoint | Excluded | Large generated binary artifact (`*.pth`). |
| `auth/users.json` | Excluded | Private local authentication hashes. |
| `.venv/` | Excluded | Local machine environment files. |
| Prediction history | Tracked (Flaw) | Intended to be local user data, but currently tracked in Git (missing from `.gitignore`). |

## 14. Fresh Setup Checklist
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Activate environment
- [ ] Install requirements
- [ ] Obtain dataset if training/evaluation is required
- [ ] Place dataset in required location (`data/raw/`)
- [ ] Obtain trained checkpoint
- [ ] Place checkpoint in `models/`
- [ ] Launch Streamlit
- [ ] Complete first-user setup if required
- [ ] Log in
- [ ] Upload test image
- [ ] Generate model output
- [ ] Verify Grad-CAM
- [ ] Verify image quality
- [ ] Verify prediction history

## 15. Troubleshooting
- **Streamlit Startup Problem**: Ensure the virtual environment is activated and `pip install -r requirements.txt` completed without errors.
- **Missing Model Checkpoint**: The application will likely throw a FileNotFoundError when loading `app.py`. Place `best_finetuned_model.pth` in the `models/` folder.
- **Authentication File Missing**: The system automatically triggers the first-user setup flow to regenerate it.
- **History File Missing**: The application is configured to create `history/prediction_history.csv` if it does not already exist when logging the first prediction.

## 16. Reproducibility Limitations
- The raw dataset is not in Git.
- The trained checkpoint is not in Git.
- Exact training environment reproduction depends entirely on `requirements.txt`.
- Consequently, full application capability from a fresh `git clone` alone is impossible without manual acquisition of the required ML artifacts. These are intentional repository design choices favoring storage hygiene and licensing compliance over instant deployment.

## 17. Privacy and Local Data Handling
This architecture actively defends local privacy:
- `auth/users.json` is excluded from Git to prevent accidental credential pushes.
- Passwords are encrypted via PBKDF2-HMAC-SHA256; plaintext passwords are never stored.
- Local application data and session states remain permanently on the host machine.

## 18. Summary
The Offline Skin Lesion Analyzer successfully documents its execution environment via `requirements.txt` and its training methodology via `src/` scripts. While the codebase is fully transparent, operational reproducibility heavily relies on the user independently supplying the underlying HAM10000 dataset and generating (or receiving) the EfficientNet-B0 checkpoint locally.
