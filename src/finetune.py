import os
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import time
from torchvision import transforms
from torch.utils.data import DataLoader

from dataset import SkinLesionDataset
from model import create_model, unfreeze_last_layers, count_parameters

# =================================================================================
# FINE-TUNING CONFIGURATION
# =================================================================================
FINETUNE_EPOCHS = 3
LEARNING_RATE = 0.00001
WEIGHT_DECAY = 0.0001
BATCH_SIZE = 16

# Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = DATA_DIR / "raw" / "images"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

TRAIN_CSV = PROCESSED_DIR / "train.csv"
VAL_CSV = PROCESSED_DIR / "val.csv"

BEST_MODEL_PATH = MODELS_DIR / "best_model.pth"
BEST_FINETUNED_MODEL_PATH = MODELS_DIR / "best_finetuned_model.pth"
HISTORY_CSV_PATH = REPORTS_DIR / "finetuning_history.csv"
CURVES_PNG_PATH = REPORTS_DIR / "finetuning_curves.png"

# =================================================================================
# BEGINNER-FRIENDLY EDUCATIONAL NOTES
# =================================================================================
# 1. Fine-tuning vs Training:
#    Training from scratch initializes random weights. Fine-tuning takes an already 
#    trained network (our previous checkpoint) and gently adjusts it for better performance.
# 
# 2. Frozen Layers:
#    We keep the majority of the network (the early and middle feature extractors) "frozen" 
#    (requires_grad = False). This ensures we don't destroy the basic edge and shape detection 
#    it already learned.
#
# 3. Unfrozen Layers:
#    We only unfreeze the final feature block(s) and the classifier. These layers contain the 
#    highest-level concepts, which we want to adjust to better recognize skin lesions.
#
# 4. Learning Rate:
#    Notice that our learning rate (0.00001) is smaller than what is typically used 
#    for initial training. A large learning rate would aggressively change weights and 
#    ruin the already good checkpoint. We just want to "fine-tune" the weights.
#
# 5. Untouched Test Set:
#    We DO NOT load or evaluate the test set here. The test set represents real-world 
#    unseen data and must only be touched at the very end of our experiments.
# =================================================================================

def calculate_metrics(tp, tn, fp, fn):
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return accuracy, precision, recall, f1

def calculate_roc_auc(y_true, y_scores):
    # Using sklearn for ROC-AUC
    from sklearn.metrics import roc_auc_score
    try:
        return roc_auc_score(y_true, y_scores)
    except ValueError:
        return 0.0

def get_dataloaders():
    # Define transforms locally to avoid loading test.csv through create_dataloaders
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dataset = SkinLesionDataset(csv_file=TRAIN_CSV, images_dir=IMAGES_DIR, transform=train_transform)
    val_dataset = SkinLesionDataset(csv_file=VAL_CSV, images_dir=IMAGES_DIR, transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    return train_loader, val_loader, len(train_dataset), len(val_dataset)

def plot_curves(history_df, save_path):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 5))

    # Loss subplot
    plt.subplot(1, 2, 1)
    plt.plot(history_df['epoch'], history_df['train_loss'], label='Train Loss')
    plt.plot(history_df['epoch'], history_df['val_loss'], label='Val Loss')
    plt.title('Loss over Epochs (Fine-tuning)')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    # ROC-AUC subplot
    plt.subplot(1, 2, 2)
    plt.plot(history_df['epoch'], history_df['val_auc'], label='Val ROC-AUC', color='green')
    plt.title('Validation ROC-AUC (Fine-tuning)')
    plt.xlabel('Epoch')
    plt.ylabel('ROC-AUC')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def main():
    # 1. Device Configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 2. Random Seeds for Reproducibility
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    # 3. Calculate positive class weight dynamically
    train_df = pd.read_csv(TRAIN_CSV)
    pos_count = len(train_df[train_df['binary_label'] == 1])
    neg_count = len(train_df[train_df['binary_label'] == 0])
    pos_weight_val = neg_count / pos_count if pos_count > 0 else 1.0
    pos_weight = torch.tensor([pos_weight_val], device=device)

    # 4. Load Data
    train_loader, val_loader, num_train, num_val = get_dataloaders()

    # 5. Create Model & Load Checkpoint
    model = create_model()
    
    if not BEST_MODEL_PATH.exists():
        print(f"Error: Initial checkpoint not found at {BEST_MODEL_PATH}")
        return
        
    checkpoint = torch.load(BEST_MODEL_PATH, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    print("✓ Successfully loaded initial model checkpoint.")

    # 6. Apply Fine-tuning Strategy
    # model backbone was frozen in create_model, so we unfreeze only the last layers
    unfreeze_last_layers(model)
    model = model.to(device)

    total_params, trainable_params = count_parameters(model)
    
    # Print trainable parameter names to verify exactly what is trainable
    print("\nTrainable parameters:")
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(f"  - {name}")

    # 7. Print Configuration
    print("\n=== Fine-Tuning Configuration ===")
    print(f"Device:                {device}")
    print(f"Training samples:      {num_train}")
    print(f"Validation samples:    {num_val}")
    print(f"Positive samples:      {pos_count}")
    print(f"Negative samples:      {neg_count}")
    print(f"Positive class weight: {pos_weight_val:.4f}")
    print(f"Total parameters:      {total_params:,}")
    print(f"Trainable parameters:  {trainable_params:,}")
    print(f"Learning rate:         {LEARNING_RATE}")
    print(f"Batch size:            {BATCH_SIZE}")
    print(f"Epochs:                {FINETUNE_EPOCHS}")
    print("=================================")

    # 8. Setup Loss and Optimizer
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), 
                            lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)

    # 9. Training Loop
    history = []
    best_val_auc = 0.0

    for epoch in range(1, FINETUNE_EPOCHS + 1):
        print(f"\n[Epoch {epoch}/{FINETUNE_EPOCHS}] starting...")
        
        # --- Training Phase ---
        model.train()
        train_loss = 0.0
        train_tp, train_tn, train_fp, train_fn = 0, 0, 0, 0
        
        train_pbar = tqdm(train_loader, desc=f"Training", leave=False)
        for images, labels in train_pbar:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images).squeeze(1)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * images.size(0)
            
            # Metrics
            probs = torch.sigmoid(outputs)
            preds = (probs >= 0.5).float()
            
            train_tp += ((preds == 1) & (labels == 1)).sum().item()
            train_tn += ((preds == 0) & (labels == 0)).sum().item()
            train_fp += ((preds == 1) & (labels == 0)).sum().item()
            train_fn += ((preds == 0) & (labels == 1)).sum().item()
            
        train_loss = train_loss / num_train
        train_acc, train_prec, train_rec, train_f1 = calculate_metrics(train_tp, train_tn, train_fp, train_fn)

        # --- Validation Phase ---
        model.eval()
        val_loss = 0.0
        val_tp, val_tn, val_fp, val_fn = 0, 0, 0, 0
        all_val_labels = []
        all_val_probs = []
        
        val_pbar = tqdm(val_loader, desc=f"Validation", leave=False)
        with torch.no_grad():
            for images, labels in val_pbar:
                images, labels = images.to(device), labels.to(device)
                
                outputs = model(images).squeeze(1)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * images.size(0)
                
                probs = torch.sigmoid(outputs)
                preds = (probs >= 0.5).float()
                
                val_tp += ((preds == 1) & (labels == 1)).sum().item()
                val_tn += ((preds == 0) & (labels == 0)).sum().item()
                val_fp += ((preds == 1) & (labels == 0)).sum().item()
                val_fn += ((preds == 0) & (labels == 1)).sum().item()
                
                all_val_labels.extend(labels.cpu().numpy())
                all_val_probs.extend(probs.cpu().numpy())
                
        val_loss = val_loss / num_val
        val_acc, val_prec, val_rec, val_f1 = calculate_metrics(val_tp, val_tn, val_fp, val_fn)
        val_auc = calculate_roc_auc(all_val_labels, all_val_probs)

        print(f"Train Loss: {train_loss:.4f} | Acc: {train_acc:.4f} | Prec: {train_prec:.4f} | Rec: {train_rec:.4f} | F1: {train_f1:.4f}")
        print(f"Val Loss:   {val_loss:.4f} | Acc: {val_acc:.4f} | Prec: {val_prec:.4f} | Rec: {val_rec:.4f} | F1: {val_f1:.4f} | AUC: {val_auc:.4f}")

        # Record History
        history.append({
            'epoch': epoch,
            'train_loss': train_loss,
            'train_accuracy': train_acc,
            'train_precision': train_prec,
            'train_recall': train_rec,
            'train_f1': train_f1,
            'val_loss': val_loss,
            'val_accuracy': val_acc,
            'val_precision': val_prec,
            'val_recall': val_rec,
            'val_f1': val_f1,
            'val_auc': val_auc
        })

        # Save Best Model
        if val_auc > best_val_auc:
            best_val_auc = val_auc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_val_auc': best_val_auc,
                'positive_class_weight': pos_weight_val
            }, BEST_FINETUNED_MODEL_PATH)
            print(f"✓ Saved new best fine-tuned model (Val AUC: {best_val_auc:.4f})")

    # 10. Save History and Plots
    history_df = pd.DataFrame(history)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    history_df.to_csv(HISTORY_CSV_PATH, index=False)
    plot_curves(history_df, CURVES_PNG_PATH)

    # 11. Final Print
    print("\n=== Fine-Tuning Completed ===")
    print(f"Best validation ROC-AUC: {best_val_auc:.4f}")
    print(f"Saved model path:        {BEST_FINETUNED_MODEL_PATH}")
    print(f"History path:            {HISTORY_CSV_PATH}")
    print(f"Curves path:             {CURVES_PNG_PATH}")

if __name__ == "__main__":
    main()
