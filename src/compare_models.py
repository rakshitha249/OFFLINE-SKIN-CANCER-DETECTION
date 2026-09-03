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

# Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = DATA_DIR / "raw" / "images"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

TEST_CSV = PROCESSED_DIR / "test.csv"
BASELINE_MODEL_PATH = MODELS_DIR / "best_model.pth"
FINETUNED_MODEL_PATH = MODELS_DIR / "best_finetuned_model.pth"

COMPARISON_CSV = REPORTS_DIR / "model_comparison.csv"
COMBINED_ROC_PNG = REPORTS_DIR / "baseline_vs_finetuned_roc.png"
METRICS_BAR_PNG = REPORTS_DIR / "baseline_vs_finetuned_metrics.png"

BATCH_SIZE = 16

def evaluate_model(model, dataloader, device):
    all_true_labels = []
    all_probs = []
    all_preds = []
    
    model.eval()
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Evaluating", leave=False):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images).squeeze(1)
            probs = torch.sigmoid(outputs)
            preds = (probs >= 0.5).float()
            
            all_true_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())
            
    return all_true_labels, all_probs, all_preds

def calculate_metrics(true_labels, probs, preds):
    cm = confusion_matrix(true_labels, preds)
    tn, fp, fn, tp = cm.ravel()
    
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    fpr, tpr, _ = roc_curve(true_labels, probs)
    roc_auc = auc(fpr, tpr)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'specificity': specificity,
        'f1': f1,
        'roc_auc': roc_auc,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'tp': tp,
        'fpr_curve': fpr,
        'tpr_curve': tpr
    }

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # 1. Dataset & DataLoader (identical to evaluate.py)
    test_df = pd.read_csv(TEST_CSV)
    num_test_samples = len(test_df)
    print(f"Total test images: {num_test_samples}")
    
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    test_dataset = SkinLesionDataset(csv_file=TEST_CSV, images_dir=IMAGES_DIR, transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    # 2. Evaluate Baseline Model
    print("\n--- Evaluating Baseline Model ---")
    baseline_model = create_model().to(device)
    baseline_model.load_state_dict(torch.load(BASELINE_MODEL_PATH, map_location=device)['model_state_dict'])
    true_labels_b, probs_b, preds_b = evaluate_model(baseline_model, test_loader, device)
    metrics_baseline = calculate_metrics(true_labels_b, probs_b, preds_b)
    
    # 3. Evaluate Fine-tuned Model
    print("\n--- Evaluating Fine-tuned Model ---")
    finetuned_model = create_model().to(device)
    finetuned_model.load_state_dict(torch.load(FINETUNED_MODEL_PATH, map_location=device)['model_state_dict'])
    true_labels_f, probs_f, preds_f = evaluate_model(finetuned_model, test_loader, device)
    metrics_finetuned = calculate_metrics(true_labels_f, probs_f, preds_f)
    
    # 4. Save CSV
    os.makedirs(REPORTS_DIR, exist_ok=True)
    comparison_df = pd.DataFrame([
        {'model': 'baseline', **{k: v for k, v in metrics_baseline.items() if not k.endswith('_curve')}},
        {'model': 'finetuned', **{k: v for k, v in metrics_finetuned.items() if not k.endswith('_curve')}}
    ])
    comparison_df.to_csv(COMPARISON_CSV, index=False)
    
    # 5. Plot Combined ROC Curve
    plt.figure(figsize=(8, 6))
    plt.plot(metrics_baseline['fpr_curve'], metrics_baseline['tpr_curve'], color='blue', lw=2, 
             label=f"Baseline (AUC = {metrics_baseline['roc_auc']:.4f})")
    plt.plot(metrics_finetuned['fpr_curve'], metrics_finetuned['tpr_curve'], color='darkorange', lw=2, 
             label=f"Fine-tuned (AUC = {metrics_finetuned['roc_auc']:.4f})")
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate (Sensitivity)')
    plt.title('Baseline vs Fine-tuned ROC Curve')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(COMBINED_ROC_PNG)
    plt.close()
    
    # 6. Plot Metrics Bar Chart
    metrics_to_plot = ['accuracy', 'precision', 'recall', 'specificity', 'f1', 'roc_auc']
    labels = ['Accuracy', 'Precision', 'Recall', 'Specificity', 'F1-score', 'ROC-AUC']
    
    baseline_vals = [metrics_baseline[m] for m in metrics_to_plot]
    finetuned_vals = [metrics_finetuned[m] for m in metrics_to_plot]
    
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, baseline_vals, width, label='Baseline', color='blue')
    rects2 = ax.bar(x + width/2, finetuned_vals, width, label='Fine-tuned', color='darkorange')
    
    ax.set_ylabel('Score')
    ax.set_title('Baseline vs Fine-tuned Performance Metrics')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='lower right')
    ax.set_ylim([0.0, 1.05])
    
    # Add values on top of bars
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
                    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(METRICS_BAR_PNG)
    plt.close()
    
    print("\n✓ Comparison completed successfully.")
    print(f"✓ Saved comparison CSV to: {COMPARISON_CSV}")
    print(f"✓ Saved combined ROC to: {COMBINED_ROC_PNG}")
    print(f"✓ Saved metrics bar chart to: {METRICS_BAR_PNG}")
    
    # Print comparison table
    print("\n--- Comparison Table ---")
    pd.set_option('display.max_columns', None)
    print(comparison_df.round(4).to_string(index=False))

if __name__ == "__main__":
    main()
