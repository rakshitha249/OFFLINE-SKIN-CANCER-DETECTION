import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from pathlib import Path

def main():
    # Setup paths
    project_root = Path(__file__).resolve().parent.parent
    reports_dir = project_root / "reports"
    predictions_csv = reports_dir / "test_predictions.csv"
    
    output_csv = reports_dir / "threshold_analysis.csv"
    metrics_png = reports_dir / "threshold_vs_metrics.png"
    error_rates_png = reports_dir / "threshold_vs_error_rates.png"
    confusion_png = reports_dir / "threshold_confusion_counts.png"
    
    print(f"Loading predictions from: {predictions_csv}")
    df = pd.read_csv(predictions_csv)
    
    # 2. Verify required columns exist
    assert 'true_label' in df.columns, "Missing 'true_label' column!"
    assert 'probability' in df.columns, "Missing 'probability' column!"
    print("✓ Required columns 'true_label' and 'probability' exist.")
    
    # 3. Verify exactly 1,494 test predictions
    total_samples = len(df)
    assert total_samples == 1494, f"Expected 1494 samples, found {total_samples}"
    print(f"✓ Total samples: {total_samples}")
    
    # 4. Verify the labels distribution
    num_neg = (df['true_label'] == 0).sum()
    num_pos = (df['true_label'] == 1).sum()
    assert num_neg == 1176, f"Expected 1176 negative samples, found {num_neg}"
    assert num_pos == 318, f"Expected 318 positive samples, found {num_pos}"
    print(f"✓ Labels verified: {num_neg} negatives, {num_pos} positives.")
    
    # 5. Verify probabilities are between 0 and 1
    assert df['probability'].between(0, 1).all(), "Found probabilities outside [0, 1]!"
    print("✓ All probabilities are between 0.0 and 1.0.")
    
    # 6. Evaluate thresholds
    thresholds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    results = []
    
    for t in thresholds:
        preds = (df['probability'] >= t).astype(int)
        cm = confusion_matrix(df['true_label'], preds)
        
        # Handle cases where confusion matrix might not be 2x2 if predictions are uniform
        if cm.shape == (1, 1):
            if preds[0] == 0: tn, fp, fn, tp = cm[0,0], 0, 0, 0
            else: tn, fp, fn, tp = 0, 0, 0, cm[0,0]
        elif cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
        else:
            tn, fp, fn, tp = 0, 0, 0, 0
            
        accuracy = (tp + tn) / total_samples if total_samples > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        results.append({
            'threshold': t,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'specificity': specificity,
            'f1': f1,
            'fpr': fpr,
            'fnr': fnr,
            'tn': tn,
            'fp': fp,
            'fn': fn,
            'tp': tp
        })
        
    results_df = pd.DataFrame(results)
    
    # Save CSV
    results_df.to_csv(output_csv, index=False)
    print(f"\n✓ Saved results to {output_csv}")
    
    # Plotting helper
    def add_current_threshold_line(plt_obj):
        plt_obj.axvline(x=0.50, color='gray', linestyle='--', alpha=0.7, label='Current Project Threshold (0.50)')
        
    # Plot 1: threshold_vs_metrics.png
    plt.figure(figsize=(10, 6))
    for metric, label in zip(['accuracy', 'precision', 'recall', 'specificity', 'f1'], 
                             ['Accuracy', 'Precision', 'Recall (Sensitivity)', 'Specificity', 'F1-score']):
        plt.plot(results_df['threshold'], results_df[metric], marker='o', label=label)
    
    add_current_threshold_line(plt)
    plt.title('Performance Metrics vs Classification Threshold')
    plt.xlabel('Threshold')
    plt.ylabel('Score')
    plt.xticks(thresholds)
    plt.ylim([0, 1.05])
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(metrics_png)
    plt.close()
    
    # Plot 2: threshold_vs_error_rates.png
    plt.figure(figsize=(8, 5))
    plt.plot(results_df['threshold'], results_df['fpr'], marker='o', color='red', label='False Positive Rate (FPR)')
    plt.plot(results_df['threshold'], results_df['fnr'], marker='o', color='blue', label='False Negative Rate (FNR)')
    
    add_current_threshold_line(plt)
    plt.title('Error Rates vs Classification Threshold')
    plt.xlabel('Threshold')
    plt.ylabel('Rate')
    plt.xticks(thresholds)
    plt.ylim([0, 1.05])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(error_rates_png)
    plt.close()
    
    # Plot 3: threshold_confusion_counts.png
    plt.figure(figsize=(10, 6))
    plt.plot(results_df['threshold'], results_df['tp'], marker='o', color='green', label='True Positives (TP)')
    plt.plot(results_df['threshold'], results_df['tn'], marker='o', color='blue', label='True Negatives (TN)')
    plt.plot(results_df['threshold'], results_df['fp'], marker='o', color='red', label='False Positives (FP)')
    plt.plot(results_df['threshold'], results_df['fn'], marker='o', color='orange', label='False Negatives (FN)')
    
    add_current_threshold_line(plt)
    plt.title('Confusion Matrix Counts vs Classification Threshold')
    plt.xlabel('Threshold')
    plt.ylabel('Count')
    plt.xticks(thresholds)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(confusion_png)
    plt.close()
    
    print(f"✓ Generated and saved 3 plots to {reports_dir}")
    
    # Print table
    print("\n=== Complete Threshold Table ===")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(results_df.round(4).to_string(index=False))

if __name__ == "__main__":
    main()
