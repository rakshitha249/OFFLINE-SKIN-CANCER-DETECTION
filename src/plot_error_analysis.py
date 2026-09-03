import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    # Setup paths
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "reports" / "error_analysis.csv"
    reports_dir = project_root / "reports"
    
    # 1. Load data
    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # 2. Validation
    total = len(df)
    fp = len(df[df['error_type'] == 'False Positive'])
    fn = len(df[df['error_type'] == 'False Negative'])
    tp = len(df[df['error_type'] == 'Correct Positive'])
    tn = len(df[df['error_type'] == 'Correct Negative'])
    correct = tp + tn
    
    assert total == 1494, f"Expected 1494 total records, found {total}"
    assert fp == 442, f"Expected 442 FP, found {fp}"
    assert fn == 29, f"Expected 29 FN, found {fn}"
    assert correct == 1023, f"Expected 1023 correct, found {correct}"
    assert tn == 734, f"Expected 734 TN, found {tn}"
    assert tp == 289, f"Expected 289 TP, found {tp}"
    print("✓ All validation counts passed perfectly.")
    
    # Define colors
    colors = {
        'Correct Positive': 'green',
        'Correct Negative': 'blue',
        'False Positive': 'red',
        'False Negative': 'orange'
    }
    
    # Plot 1: error_probability_distribution.png
    plt.figure(figsize=(12, 7))
    for err_type, color in colors.items():
        subset = df[df['error_type'] == err_type]['probability']
        if not subset.empty:
            plt.hist(subset, bins=50, alpha=0.5, density=False, label=err_type, color=color)
            
    plt.axvline(x=0.5, color='gray', linestyle='--', label='Decision Threshold (0.5)')
    plt.title('Probability Distribution by Error Type')
    plt.xlabel('Predicted Malignant-Suspicious Probability')
    plt.ylabel('Number of Samples')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(reports_dir / "error_probability_distribution.png")
    plt.close()
    
    # Plot 2: error_probability_by_class.png
    plt.figure(figsize=(10, 6))
    classes = ['NV', 'BKL', 'MEL', 'BCC', 'AKIEC', 'DF', 'VASC']
    
    plot_data = [df[df['original_class'] == cls]['probability'].values for cls in classes]
    
    plt.boxplot(plot_data, tick_labels=classes, patch_artist=True)
    plt.axhline(y=0.5, color='gray', linestyle='--', label='Decision Threshold (0.5)')
    plt.title('Predicted Probability Distribution by Original Class')
    plt.xlabel('Original HAM10000 Class')
    plt.ylabel('Predicted Malignant-Suspicious Probability')
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(reports_dir / "error_probability_by_class.png")
    plt.close()
    
    # Plot 3: errors_by_original_class.png
    err_df = df[df['error_type'].isin(['False Positive', 'False Negative'])]
    err_grouped = err_df.groupby(['original_class', 'error_type']).size().unstack(fill_value=0)
    
    # Ensure both columns exist even if 0
    if 'False Positive' not in err_grouped.columns:
        err_grouped['False Positive'] = 0
    if 'False Negative' not in err_grouped.columns:
        err_grouped['False Negative'] = 0
        
    err_grouped = err_grouped[['False Positive', 'False Negative']] # Ensure order
    
    ax = err_grouped.plot(kind='bar', figsize=(10, 6), color=['red', 'orange'], width=0.8)
    plt.title('Error Counts by Original Class')
    plt.xlabel('Original Class')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    plt.legend(title='Error Type')
    plt.grid(True, axis='y', alpha=0.3)
    
    # Add values on top
    for container in ax.containers:
        ax.bar_label(container, padding=3)
        
    plt.tight_layout()
    plt.savefig(reports_dir / "errors_by_original_class.png")
    plt.close()
    
    # Plot 4: error_probability_ranges.png
    bins = np.arange(0.0, 1.1, 0.1)
    labels = [f"{bins[i]:.2f}-{bins[i+1]:.2f}" for i in range(len(bins)-1)]
    
    fp_probs = df[df['error_type'] == 'False Positive']['probability']
    fn_probs = df[df['error_type'] == 'False Negative']['probability']
    
    fp_counts, _ = np.histogram(fp_probs, bins=bins)
    fn_counts, _ = np.histogram(fn_probs, bins=bins)
    
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, fp_counts, width, label='False Positive', color='red')
    rects2 = ax.bar(x + width/2, fn_counts, width, label='False Negative', color='orange')
    
    ax.set_ylabel('Count')
    ax.set_title('Errors by Probability Range')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45)
    ax.legend()
    
    for container in ax.containers:
        ax.bar_label(container, padding=3)
        
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(reports_dir / "error_probability_ranges.png")
    plt.close()
    
    print("✓ Successfully generated all 4 plots.")

if __name__ == '__main__':
    main()
