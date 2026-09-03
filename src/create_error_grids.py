import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path
import os

def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / 'reports' / 'selected_error_images.csv'
    images_dir = project_root / 'data' / 'raw' / 'images'
    reports_dir = project_root / 'reports'
    
    print(f"Loading data from {csv_path}")
    df = pd.read_csv(csv_path)
    
    categories = [
        ('A_high_confidence_FP', 'A — High-Confidence False Positives'),
        ('B_borderline_FP', 'B — Borderline False Positives'),
        ('C_borderline_FN', 'C — Borderline False Negatives'),
        ('D_low_probability_FN', 'D — Low-Probability False Negatives')
    ]
    
    for cat_key, cat_title in categories:
        cat_df = df[df['selection_category'] == cat_key]
        
        # Verify exactly 5 images
        assert len(cat_df) == 5, f"Expected 5 images for {cat_key}, found {len(cat_df)}"
        
        fig, axes = plt.subplots(1, 5, figsize=(25, 6))
        fig.suptitle(cat_title, fontsize=20, y=1.05)
        
        image_ids_included = []
        
        for idx, (_, row) in enumerate(cat_df.iterrows()):
            img_id = row['image_id']
            prob = row['probability']
            orig_class = row['original_class']
            err_type = row['error_type']
            
            img_path = images_dir / f"{img_id}.jpg"
            assert img_path.exists(), f"Missing image file: {img_path}"
            
            image_ids_included.append(img_id)
            
            img = mpimg.imread(str(img_path))
            
            ax = axes[idx]
            ax.imshow(img)
            ax.axis('off')
            
            title_text = f"ID: {img_id}\nProb: {prob:.4f}\nClass: {orig_class}\nType: {err_type}"
            ax.set_title(title_text, fontsize=12, pad=10)
            
        plt.tight_layout()
        out_filename = f"error_grid_{cat_key}.png"
        out_path = reports_dir / out_filename
        plt.savefig(out_path, dpi=200, bbox_inches='tight')
        plt.close()
        
        print(f"Generated: {out_filename}")
        print(f"  - Images (5): {', '.join(image_ids_included)}")
        assert out_path.exists(), f"Failed to save {out_filename}"

    print("\n✓ All 4 error grids successfully created and verified.")

if __name__ == "__main__":
    main()
