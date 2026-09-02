import os
import torch
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from torchvision import transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc, confusion_matrix

from dataset import SkinLesionDataset
from model import create_model

# =================================================================================
# BEGINNER-FRIENDLY EDUCATIONAL NOTES: EVALUATION
# =================================================================================
# 1. Why the Test Set is Used Only Once:
#    The test set represents real-world, unseen data. If we look at the test set
#    performance and tweak our model (e.g., change the threshold or learning rate) 
#    based on it, we are "leaking" information from the test set into the model.
#    It would no longer be an unbiased estimate of real-world performance!
#
# 2. Confusion Matrix:
#    A grid that shows the combinations of actual vs. predicted classes:
#    - True Positive (TP): Model correctly predicted malignant.
#    - True Negative (TN): Model correctly predicted benign.
#    - False Positive (FP): Model predicted malignant, but it was benign (False Alarm).
#    - False Negative (FN): Model predicted benign, but it was malignant (Missed Disease).
#
# 3. Sensitivity (Recall):
#    Of all the *actual* malignant lesions, how many did we correctly identify?
#    Formula: TP / (TP + FN)
#    In medicine, high sensitivity is crucial so we don't miss cancers.
#
# 4. Specificity:
#    Of all the *actual* benign lesions, how many did we correctly identify?
#    Formula: TN / (TN + FP)
#    High specificity means we don't unnecessarily alarm healthy patients.
#
# 5. ROC-AUC:
#    Receiver Operating Characteristic - Area Under the Curve.
#    It measures the model's ability to distinguish between malignant and benign
#    across ALL possible thresholds (not just 0.5).
#    That's why we use raw probabilities (0.0 to 1.0) rather than thresholded 
#    predictions (0 or 1) to calculate it.
# =================================================================================

# Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = DATA_DIR / "raw" / "images"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

TEST_CSV = PROCESSED_DIR / "test.csv"
BEST_FINETUNED_MODEL_PATH = MODELS_DIR / "best_finetuned_model.pth"

TEST_METRICS_CSV = REPORTS_DIR / "test_metrics.csv"
CONFUSION_MATRIX_PNG = REPORTS_DIR / "confusion_matrix.png"
ROC_CURVE_PNG = REPORTS_DIR / "roc_curve.png"
TEST_PREDICTIONS_CSV = REPORTS_DIR / "test_predictions.csv"

BATCH_SIZE = 16

def plot_confusion_matrix(cm, save_path):
    fig, ax = plt.subplots(figsize=(6, 5))
    cax = ax.matshow(cm, cmap='Blues')
    plt.colorbar(cax)
    
    # Add text annotations
    for (i, j), val in np.ndenumerate(cm):
        ax.text(j, i, f'{val}', ha='center', va='center', color='black' if val < cm.max()/2 else 'white')
        
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Benign (0)', 'Malignant (1)'])
    ax.set_yticklabels(['Benign (0)', 'Malignant (1)'])
    ax.xaxis.set_ticks_position('bottom')
    
    plt.title('Confusion Matrix', pad=20)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_roc_curve(fpr, tpr, roc_auc, save_path):
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate (Sensitivity)')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def main():
    # 1. Device Configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # 2. Load and Verify Test Dataset
    test_df = pd.read_csv(TEST_CSV)
    num_test_samples = len(test_df)
    
    print(f"\nTotal test images found: {num_test_samples}")
    
    if num_test_samples != 1494:
        print(f"Warning: Expected exactly 1494 test images, but found {num_test_samples}.")
    else:
        print("✓ Verified exactly 1494 test images.")
        
    if test_df['image_id'].duplicated().any():
        print("Warning: Duplicate image IDs found in the test set!")
    else:
        print("✓ Verified no duplicate test image IDs.")

    # 3. Create Dataset and DataLoader
    # Validation/Test transforms ONLY (No augmentation)
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    test_dataset = SkinLesionDataset(csv_file=TEST_CSV, images_dir=IMAGES_DIR, transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # 4. Load Model
    if not BEST_FINETUNED_MODEL_PATH.exists():
        print(f"Error: Fine-tuned model checkpoint not found at {BEST_FINETUNED_MODEL_PATH}")
        return

    model = create_model()
    checkpoint = torch.load(BEST_FINETUNED_MODEL_PATH, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    print("✓ Successfully loaded fine-tuned model checkpoint.")

    # 5. Evaluate
    print("\nStarting evaluation on the test set...")
    all_image_ids = []
    all_true_labels = []
    all_probs = []
    all_preds = []
    
    # We retrieve image_ids directly from the DataFrame using idx
    # since DataLoader doesn't return them by default. 
    # Because shuffle=False, the order matches the DataFrame exactly.
    
    test_pbar = tqdm(test_loader, desc="Evaluating", leave=False)
    
    with torch.no_grad():
        for images, labels in test_pbar:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images).squeeze(1)
            probs = torch.sigmoid(outputs)
            
            # Default threshold of 0.5
            preds = (probs >= 0.5).float()
            
            all_true_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    all_image_ids = test_df['image_id'].tolist()

    # 6. Calculate Metrics
    # TP, TN, FP, FN
    cm = confusion_matrix(all_true_labels, all_preds)
    # cm format:
    # [[TN, FP],
    #  [FN, TP]]
    tn, fp, fn, tp = cm.ravel()

    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    # ROC-AUC using raw probabilities
    fpr, tpr, thresholds = roc_curve(all_true_labels, all_probs)
    roc_auc = auc(fpr, tpr)

    # 7. Print Results
    print("\n=== Final Test Set Evaluation ===")
    print(f"Evaluated Images: {len(all_true_labels)}")
    print(f"Accuracy:         {accuracy:.4f}")
    print(f"Precision:        {precision:.4f}")
    print(f"Recall (Sens.):   {recall:.4f}")
    print(f"Specificity:      {specificity:.4f}")
    print(f"F1 Score:         {f1:.4f}")
    print(f"ROC-AUC:          {roc_auc:.4f}")
    print("\nConfusion Matrix:")
    print(f"[[{tn}, {fp}],")
    print(f" [{fn}, {tp}]]")
    print("=================================")

    # 8. Save Artifacts
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Save Predictions CSV
    predictions_df = pd.DataFrame({
        'image_id': all_image_ids,
        'true_label': all_true_labels,
        'predicted_label': all_preds,
        'probability': all_probs
    })
    # Convert labels back to int for cleaner CSV presentation
    predictions_df['true_label'] = predictions_df['true_label'].astype(int)
    predictions_df['predicted_label'] = predictions_df['predicted_label'].astype(int)
    predictions_df.to_csv(TEST_PREDICTIONS_CSV, index=False)
    
    # Save Metrics CSV
    metrics_df = pd.DataFrame([{
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'sensitivity': sensitivity,
        'specificity': specificity,
        'f1': f1,
        'roc_auc': roc_auc,
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn
    }])
    metrics_df.to_csv(TEST_METRICS_CSV, index=False)
    
    # Save Visualizations
    plot_confusion_matrix(cm, CONFUSION_MATRIX_PNG)
    plot_roc_curve(fpr, tpr, roc_auc, ROC_CURVE_PNG)
    
    print("\n✓ Saved test predictions to: reports/test_predictions.csv")
    print("✓ Saved final metrics to:    reports/test_metrics.csv")
    print("✓ Saved confusion matrix to: reports/confusion_matrix.png")
    print("✓ Saved ROC curve to:        reports/roc_curve.png")

if __name__ == "__main__":
    main()
