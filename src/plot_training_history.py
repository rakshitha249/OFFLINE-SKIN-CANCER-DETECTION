import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent.parent
    reports_dir = project_root / "reports"
    
    train_csv = reports_dir / "training_history.csv"
    finetune_csv = reports_dir / "finetuning_history.csv"
    
    # Read both CSVs
    df_train = pd.read_csv(train_csv)
    df_finetune = pd.read_csv(finetune_csv)
    
    # Adjust epoch numbers for finetuning to make them continuous
    last_train_epoch = df_train['epoch'].max()
    df_finetune['epoch'] = df_finetune['epoch'] + last_train_epoch
    
    # Combine into a single history dataframe
    df = pd.concat([df_train, df_finetune], ignore_index=True)
    
    # Define a helper plotting function
    def plot_metric(metric_train, metric_val, title, ylabel, save_name, only_val=False):
        plt.figure(figsize=(8, 6))
        if not only_val:
            plt.plot(df['epoch'], df[metric_train], marker='o', label=f'Training {ylabel}')
        plt.plot(df['epoch'], df[metric_val], marker='o', label=f'Validation {ylabel}')
        
        # Add a vertical line to indicate where fine-tuning started
        plt.axvline(x=last_train_epoch + 0.5, color='gray', linestyle='--', label='Fine-tuning starts')
        
        plt.title(title)
        plt.xlabel('Epoch')
        plt.ylabel(ylabel)
        plt.xticks(df['epoch'])
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(reports_dir / save_name)
        plt.close()

    # 1. Loss
    plot_metric('train_loss', 'val_loss', 'Training and Validation Loss', 'Loss', 'training_validation_loss.png')
    
    # 2. Accuracy
    plot_metric('train_accuracy', 'val_accuracy', 'Training and Validation Accuracy', 'Accuracy', 'training_validation_accuracy.png')
    
    # 3. Precision
    plot_metric('train_precision', 'val_precision', 'Training and Validation Precision', 'Precision', 'training_validation_precision.png')
    
    # 4. Recall
    plot_metric('train_recall', 'val_recall', 'Training and Validation Recall', 'Recall', 'training_validation_recall.png')
    
    # 5. F1-score
    plot_metric('train_f1', 'val_f1', 'Training and Validation F1-Score', 'F1-Score', 'training_validation_f1.png')
    
    # 6. ROC-AUC (Validation only)
    plot_metric(None, 'val_auc', 'Validation ROC-AUC', 'ROC-AUC', 'validation_roc_auc.png', only_val=True)
    
    print("Plots generated successfully!")

if __name__ == "__main__":
    main()
