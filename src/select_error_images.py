import pandas as pd
import os
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / 'reports' / 'error_analysis.csv'
    out_csv = project_root / 'reports' / 'selected_error_images.csv'
    images_dir = project_root / 'data' / 'raw' / 'images'
    
    print(f"Loading data from {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Calculate distance from threshold
    df['distance_from_threshold'] = abs(df['probability'] - 0.50)
    
    # Separate FP and FN
    # Note: The CSV contains 'False Positive' and 'False Negative' strings
    fp_df = df[df['error_type'] == 'False Positive'].copy()
    fn_df = df[df['error_type'] == 'False Negative'].copy()
    
    selected_frames = []
    
    # A. High-Confidence False Positives
    a_df = fp_df.sort_values(by=['probability', 'image_id'], ascending=[False, True]).head(5).copy()
    a_df['selection_category'] = 'A_high_confidence_FP'
    selected_frames.append(a_df)
    
    # B. Borderline False Positives
    b_df = fp_df.sort_values(by=['distance_from_threshold', 'image_id'], ascending=[True, True]).head(5).copy()
    b_df['selection_category'] = 'B_borderline_FP'
    selected_frames.append(b_df)
    
    # C. Borderline False Negatives
    c_df = fn_df.sort_values(by=['distance_from_threshold', 'image_id'], ascending=[True, True]).head(5).copy()
    c_df['selection_category'] = 'C_borderline_FN'
    selected_frames.append(c_df)
    
    # D. Low-Probability False Negatives
    d_df = fn_df.sort_values(by=['probability', 'image_id'], ascending=[True, True]).head(5).copy()
    d_df['selection_category'] = 'D_low_probability_FN'
    selected_frames.append(d_df)
    
    # Combine
    final_df = pd.concat(selected_frames, ignore_index=True)
    
    # Select columns
    cols_to_keep = ['image_id', 'probability', 'true_label', 'predicted_label', 
                    'original_class', 'lesion_id', 'error_type', 'selection_category', 'distance_from_threshold']
    final_df = final_df[cols_to_keep]
    
    # Verifications
    assert len(final_df) == 20, f"Expected 20 rows, got {len(final_df)}"
    assert len(final_df['selection_category'].unique()) == 4, "Expected 4 categories"
    for cat in final_df['selection_category'].unique():
        assert len(final_df[final_df['selection_category'] == cat]) == 5, f"Expected 5 rows for {cat}"
    assert final_df['image_id'].nunique() == 20, "Duplicate image_id found in selection!"
    
    for img_id in final_df['image_id']:
        assert (images_dir / f"{img_id}.jpg").exists(), f"Image file missing for {img_id}"
        
    print("✓ All 20 selected image files exist locally.")
    print("✓ Selection contains no duplicate images.")
    print("✓ Exact 5 images per category verified.")
    
    # Save
    final_df.to_csv(out_csv, index=False)
    print(f"✓ Saved selection to {out_csv}")
    
    # Summary Table
    print("\n=== Deterministic Selection Summary ===")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    summary_cols = ['selection_category', 'image_id', 'probability', 'original_class', 'error_type']
    print(final_df[summary_cols].round(4).to_string(index=False))

if __name__ == "__main__":
    main()
