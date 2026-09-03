import pandas as pd
from pathlib import Path

def main():
    # Setup paths
    project_root = Path(__file__).resolve().parent.parent
    predictions_csv = project_root / "reports" / "test_predictions.csv"
    test_metadata_csv = project_root / "data" / "processed" / "test.csv"
    
    error_analysis_csv = project_root / "reports" / "error_analysis.csv"
    error_by_class_csv = project_root / "reports" / "error_analysis_by_class.csv"
    
    print("Loading datasets...")
    pred_df = pd.read_csv(predictions_csv)
    meta_df = pd.read_csv(test_metadata_csv)
    
    # 2. Validate image_id
    assert 'image_id' in pred_df.columns, "image_id missing in test_predictions.csv"
    assert 'image_id' in meta_df.columns, "image_id missing in test.csv"
    print("✓ 'image_id' found in both datasets.")
    
    # 3. Merge
    df = pd.merge(pred_df, meta_df, on='image_id', how='inner')
    
    # 4. Verify length
    assert len(df) == 1494, f"Merge produced {len(df)} records, expected 1494."
    print("✓ Merge produced exactly 1494 test records.")
    
    # 14. Check duplicates
    dup_ids = df['image_id'].duplicated().sum()
    assert dup_ids == 0, f"Found {dup_ids} duplicate image_ids after merge."
    print("✓ No duplicate image_ids after merge.")
    
    # 15. Check missing values
    assert df['original_class'].isnull().sum() == 0, "Missing original_class values found."
    assert df['lesion_id'].isnull().sum() == 0, "Missing lesion_id values found."
    print("✓ No missing original_class or lesion_id values.")
    
    # 5. Verify true_label matches binary_label
    assert (df['true_label'] == df['binary_label']).all(), "Mismatch between true_label and binary_label!"
    print("✓ true_label perfectly matches binary_label for all images.")
    
    # 6. Create error_type column
    def get_error_type(row):
        t = row['true_label']
        p = row['predicted_label']
        if t == 0 and p == 0: return 'Correct Negative'
        if t == 1 and p == 1: return 'Correct Positive'
        if t == 0 and p == 1: return 'False Positive'
        if t == 1 and p == 0: return 'False Negative'
        return 'Unknown'
        
    df['error_type'] = df.apply(get_error_type, axis=1)
    
    # 7. Save error_analysis.csv
    cols_to_keep = ['image_id', 'true_label', 'predicted_label', 'probability', 
                    'original_class', 'binary_class', 'lesion_id', 'error_type']
    df_out = df[cols_to_keep].copy()
    df_out.to_csv(error_analysis_csv, index=False)
    print(f"✓ Saved error analysis dataset to {error_analysis_csv}")
    
    # 8. Create summary table grouped by original_class
    summary = []
    classes = df['original_class'].unique()
    for cls in classes:
        cls_df = df[df['original_class'] == cls]
        total = len(cls_df)
        correct = len(cls_df[cls_df['error_type'].isin(['Correct Positive', 'Correct Negative'])])
        fp = len(cls_df[cls_df['error_type'] == 'False Positive'])
        fn = len(cls_df[cls_df['error_type'] == 'False Negative'])
        error_rate = (fp + fn) / total if total > 0 else 0.0
        
        summary.append({
            'original_class': cls,
            'total_samples': total,
            'correct': correct,
            'false_positives': fp,
            'false_negatives': fn,
            'error_rate': error_rate
        })
        
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(error_by_class_csv, index=False)
    print(f"✓ Saved class summary to {error_by_class_csv}")
    
    # 9. Misclassified summary
    print("\n=== Errors by Original Class ===")
    error_summary = summary_df[['original_class', 'false_positives', 'false_negatives']].copy()
    error_summary['total_errors'] = error_summary['false_positives'] + error_summary['false_negatives']
    print(error_summary.sort_values(by='total_errors', ascending=False).to_string(index=False))
    
    # 10. & 11. Verify counts
    cn_count = len(df[df['error_type'] == 'Correct Negative'])
    cp_count = len(df[df['error_type'] == 'Correct Positive'])
    fp_count = len(df[df['error_type'] == 'False Positive'])
    fn_count = len(df[df['error_type'] == 'False Negative'])
    
    total_correct = cn_count + cp_count
    total_errors = fp_count + fn_count
    
    print("\n=== Global Count Verification ===")
    print(f"Correct predictions: {total_correct} (Expected 1023)")
    print(f"False Positives: {fp_count} (Expected 442)")
    print(f"False Negatives: {fn_count} (Expected 29)")
    print(f"Total errors: {total_errors} (Expected 471)")
    
    print(f"\nTN: {cn_count} (Expected 734)")
    print(f"FP: {fp_count} (Expected 442)")
    print(f"FN: {fn_count} (Expected 29)")
    print(f"TP: {cp_count} (Expected 289)")
    
    assert total_correct == 1023, "Total correct count mismatch!"
    assert fp_count == 442, "FP count mismatch!"
    assert fn_count == 29, "FN count mismatch!"
    assert total_errors == 471, "Total errors mismatch!"
    assert cn_count == 734, "TN count mismatch!"
    assert cp_count == 289, "TP count mismatch!"
    print("✓ All counts verified perfectly.")
    
    # 13. Identify extremes
    most_fp_cls = summary_df.loc[summary_df['false_positives'].idxmax()]['original_class']
    most_fn_cls = summary_df.loc[summary_df['false_negatives'].idxmax()]['original_class']
    
    highest_err_row = summary_df.loc[summary_df['error_rate'].idxmax()]
    highest_err_cls = highest_err_row['original_class']
    highest_err_rate = highest_err_row['error_rate']
    highest_err_count = highest_err_row['total_samples']
    
    print("\n=== Error Distribution Extremes ===")
    print(f"Class with most False Positives: {most_fp_cls}")
    print(f"Class with most False Negatives: {most_fn_cls}")
    print(f"Class with highest error rate: {highest_err_cls} ({highest_err_rate:.2%} error rate, across {highest_err_count} total samples)")

if __name__ == "__main__":
    main()
