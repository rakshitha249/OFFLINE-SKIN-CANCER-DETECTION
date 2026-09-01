import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from pathlib import Path
import random
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import matplotlib.pyplot as plt
from tqdm import tqdm

from dataset import create_dataloaders
from model import create_model

# =================================================================================
# Configuration
# =================================================================================
# This is a short baseline training run, deliberately kept small to run on CPU.
INITIAL_EPOCHS = 3
BATCH_SIZE = 16
LEARNING_RATE = 0.0001
WEIGHT_DECAY = 0.0001

def set_seed(seed=42):
    """Sets random seeds for reproducibility across runs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def calculate_metrics(y_true, y_pred_prob, threshold=0.5):
    """
    Safely calculates classification metrics, handling division by zero.
    We use a default threshold of 0.5 to convert probabilities to class predictions.
    """
    y_pred_binary = (y_pred_prob >= threshold).astype(int)
    
    # zero_division=0 handles division by zero safely if the model predicts only one class
    acc = accuracy_score(y_true, y_pred_binary)
    prec = precision_score(y_true, y_pred_binary, zero_division=0)
    rec = recall_score(y_true, y_pred_binary, zero_division=0)
    f1 = f1_score(y_true, y_pred_binary, zero_division=0)
    
    # Try to calculate AUC. If only one class is present in a batch/set, it raises an error.
    try:
        auc = roc_auc_score(y_true, y_pred_prob)
    except ValueError:
        auc = 0.5  # Random performance if ROC-AUC cannot be calculated
        
    return acc, prec, rec, f1, auc

def main():
    set_seed(42)
    
    # Define paths
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    processed_dir = data_dir / "processed"
    models_dir = project_root / "models"
    reports_dir = project_root / "reports"
    
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup Device automatically
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Selected Device: {device}")
    
    # =================================================================================
    # IMPORTANT EDUCATIONAL NOTES ON POSITIVE CLASS WEIGHTING
    # =================================================================================
    # In medical datasets, we often have far more healthy/negative examples than 
    # diseased/positive examples. If a dataset is 80% negative, a model can achieve 
    # 80% accuracy by simply guessing "Negative" every single time!
    # 
    # To fix this, we calculate a "positive class weight". If negatives outnumber 
    # positives 4 to 1, we give the model a penalty that is 4 times harsher when 
    # it gets a positive example wrong. This forces the model to pay attention to 
    # the rare positive cases.
    # =================================================================================
    
    train_csv_path = processed_dir / "train.csv"
    train_df = pd.read_csv(train_csv_path)
    
    num_neg = (train_df['binary_label'] == 0).sum()
    num_pos = (train_df['binary_label'] == 1).sum()
    
    # Calculate pos_weight dynamically
    pos_weight_val = num_neg / num_pos
    pos_weight = torch.tensor([pos_weight_val], dtype=torch.float32).to(device)
    
    # Create DataLoaders
    # The test_loader is returned but NEVER used during training to prevent leakage.
    train_loader, val_loader, test_loader = create_dataloaders()
    
    # Create Model
    model = create_model()
    model = model.to(device)
    
    # Count trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # Pre-training Printouts
    print("\n--- Pre-training Information ---")
    print(f"Number of training samples: {len(train_loader.dataset)}")
    print(f"Number of validation samples: {len(val_loader.dataset)}")
    print(f"Negative samples in training (Label 0): {num_neg}")
    print(f"Positive samples in training (Label 1): {num_pos}")
    print(f"Calculated positive class weight: {pos_weight_val:.4f}")
    print(f"Number of trainable model parameters: {trainable_params:,}")
    print(f"Number of epochs: {INITIAL_EPOCHS}")
    
    # =================================================================================
    # IMPORTANT EDUCATIONAL NOTES ON LOSS AND OPTIMIZER
    # =================================================================================
    # 1. BCEWithLogitsLoss:
    #    This calculates how "wrong" the model's predictions are. It combines a 
    #    Sigmoid layer and Binary Cross Entropy Loss into one step for better numerical 
    #    stability. We pass in our pos_weight to handle the imbalanced data.
    #
    # 2. AdamW Optimizer:
    #    The optimizer is the algorithm that adjusts the model's weights to minimize 
    #    the loss. AdamW is a highly effective, modern variant of Gradient Descent 
    #    that includes "Weight Decay" (a technique that prevents weights from growing 
    #    too large, which helps prevent overfitting).
    #
    # 3. Epoch:
    #    One "epoch" means the model has looked at every single image in the training 
    #    set exactly once.
    # =================================================================================
    
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    
    # Tracking variables
    history = []
    best_val_auc = 0.0
    best_model_path = models_dir / "best_model.pth"
    
    print("\nStarting Training...\n")
    
    for epoch in range(INITIAL_EPOCHS):
        # -----------------------
        # TRAINING PHASE
        # -----------------------
        model.train()
        train_loss = 0.0
        
        all_train_preds = []
        all_train_targets = []
        
        # tqdm progress bar
        train_pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{INITIAL_EPOCHS} [Train]")
        for images, labels in train_pbar:
            images = images.to(device)
            labels = labels.to(device).unsqueeze(1) # reshape from [batch] to [batch, 1]
            
            optimizer.zero_grad()
            
            logits = model(images)
            loss = criterion(logits, labels)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * images.size(0)
            
            # Use sigmoid ONLY to convert logits to probabilities for metrics
            probs = torch.sigmoid(logits).detach().cpu().numpy()
            all_train_preds.extend(probs)
            all_train_targets.extend(labels.cpu().numpy())
            
        train_loss = train_loss / len(train_loader.dataset)
        train_acc, train_prec, train_rec, train_f1, _ = calculate_metrics(
            np.array(all_train_targets), np.array(all_train_preds)
        )
        
        # -----------------------
        # VALIDATION PHASE
        # -----------------------
        # =================================================================================
        # IMPORTANT EDUCATIONAL NOTES ON VALIDATION AND TEST SETS
        # =================================================================================
        # 1. Validation: 
        #    After every epoch, we test the model on the Validation set. The model 
        #    does NOT learn from these images. We do this to see how well the model 
        #    is generalizing to new data and to track the "Best Validation ROC-AUC".
        # 2. Why is the Test Data kept untouched?
        #    We might tweak our learning rate or pick the best epoch based on Validation 
        #    performance. This means the model indirectly "learns" from the Validation 
        #    set. The Test set must remain 100% blind to provide a completely unbiased 
        #    final grade.
        # =================================================================================
        model.eval()
        val_loss = 0.0
        
        all_val_preds = []
        all_val_targets = []
        
        val_pbar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{INITIAL_EPOCHS} [Val]  ")
        with torch.no_grad():
            for images, labels in val_pbar:
                images = images.to(device)
                labels = labels.to(device).unsqueeze(1)
                
                logits = model(images)
                loss = criterion(logits, labels)
                
                val_loss += loss.item() * images.size(0)
                
                probs = torch.sigmoid(logits).cpu().numpy()
                all_val_preds.extend(probs)
                all_val_targets.extend(labels.cpu().numpy())
                
        val_loss = val_loss / len(val_loader.dataset)
        
        # =================================================================================
        # IMPORTANT EDUCATIONAL NOTE ON ROC-AUC
        # =================================================================================
        # Receiver Operating Characteristic - Area Under Curve (ROC-AUC) is a metric 
        # from 0.0 to 1.0. It measures the model's ability to distinguish between 
        # positive and negative classes across ALL possible thresholds. 
        # 0.5 = Random guessing. 1.0 = Perfect classification. 
        # ROC-AUC is especially excellent for evaluating models on highly imbalanced datasets.
        # =================================================================================
        val_acc, val_prec, val_rec, val_f1, val_auc = calculate_metrics(
            np.array(all_val_targets), np.array(all_val_preds)
        )
        
        print(f"\nEpoch {epoch+1} Results:")
        print(f"Train - Loss: {train_loss:.4f} | Acc: {train_acc:.4f} | F1: {train_f1:.4f}")
        print(f"Val   - Loss: {val_loss:.4f} | Acc: {val_acc:.4f} | F1: {val_f1:.4f} | AUC: {val_auc:.4f}")
        
        # Save history
        history.append({
            'epoch': epoch + 1,
            'train_loss': train_loss, 'train_accuracy': train_acc, 
            'train_precision': train_prec, 'train_recall': train_rec, 'train_f1': train_f1,
            'val_loss': val_loss, 'val_accuracy': val_acc,
            'val_precision': val_prec, 'val_recall': val_rec, 'val_f1': val_f1,
            'val_auc': val_auc
        })
        
        # Track Best Model based on Validation AUC
        if val_auc > best_val_auc:
            best_val_auc = val_auc
            checkpoint = {
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_val_auc': best_val_auc,
                'positive_class_weight': pos_weight.item()
            }
            torch.save(checkpoint, best_model_path)
            print(f"-> Saved new best model (Val AUC: {best_val_auc:.4f})")
            
        print("-" * 50)
            
    # Save History CSV
    history_df = pd.DataFrame(history)
    history_csv_path = reports_dir / "training_history.csv"
    history_df.to_csv(history_csv_path, index=False)
    
    # Plot Training Curves
    curves_path = reports_dir / "training_curves.png"
    plt.figure(figsize=(15, 5))
    
    # Loss Plot
    plt.subplot(1, 3, 1)
    plt.plot(history_df['epoch'], history_df['train_loss'], label='Train Loss', marker='o')
    plt.plot(history_df['epoch'], history_df['val_loss'], label='Val Loss', marker='o')
    plt.title('Loss Curves')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    # Accuracy & AUC Plot
    plt.subplot(1, 3, 2)
    plt.plot(history_df['epoch'], history_df['train_accuracy'], label='Train Acc', marker='o')
    plt.plot(history_df['epoch'], history_df['val_accuracy'], label='Val Acc', marker='o')
    plt.plot(history_df['epoch'], history_df['val_auc'], label='Val AUC', marker='o', linestyle='--')
    plt.title('Accuracy and AUC')
    plt.xlabel('Epoch')
    plt.ylabel('Score')
    plt.legend()
    plt.grid(True)
    
    # Precision, Recall, F1 Plot
    plt.subplot(1, 3, 3)
    plt.plot(history_df['epoch'], history_df['val_precision'], label='Val Precision', marker='o')
    plt.plot(history_df['epoch'], history_df['val_recall'], label='Val Recall', marker='o')
    plt.plot(history_df['epoch'], history_df['val_f1'], label='Val F1', marker='o')
    plt.title('Validation Precision, Recall, F1')
    plt.xlabel('Epoch')
    plt.ylabel('Score')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(curves_path)
    
    # Post-training Printouts
    print("\n--- Training Completed ---")
    print(f"Best validation ROC-AUC: {best_val_auc:.4f}")
    print(f"Path to saved model: {best_model_path}")
    print(f"Path to training history: {history_csv_path}")
    print(f"Path to training curves: {curves_path}")

if __name__ == "__main__":
    main()
