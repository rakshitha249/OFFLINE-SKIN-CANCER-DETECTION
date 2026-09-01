import pandas as pd
from pathlib import Path

def main():
    # Define paths relative to the current file's location (the project root)
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"
    processed_data_dir = project_root / "data" / "processed"
    images_dir = raw_data_dir / "images"
    
    csv_path = raw_data_dir / "ISIC2018_Task3_Training_GroundTruth.csv"
    output_path = processed_data_dir / "binary_dataset.csv"
    
    # Ensure processed data directory exists before saving
    processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Read the original ground truth dataset
    print(f"Reading original dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # 2. Determine original diagnosis for each image
    classes = ['MEL', 'NV', 'BCC', 'AKIEC', 'BKL', 'DF', 'VASC']
    df['original_class'] = df[classes].idxmax(axis=1)
    
    # 3. Define mapping for the binary target. 
    # IMPORTANT RESEARCH NOTE:
    # AKIEC (Actinic keratosis / intraepithelial carcinoma) is a precancerous 
    # or in situ carcinoma. In this binary classification task meant for research 
    # and educational purposes, it is included in the "Malignant-Suspicious" 
    # category because it is highly clinically relevant to detect and monitor. 
    # Note that this mapping is a research convention to simplify the dataset 
    # and is not intended to serve as a strict clinical diagnosis.
    positive_classes = ['MEL', 'BCC', 'AKIEC']
    negative_classes = ['NV', 'BKL', 'DF', 'VASC']
    
    # 4. Assign binary label: 1 for Malignant-Suspicious, 0 for Non-malignant
    df['binary_label'] = df['original_class'].apply(lambda x: 1 if x in positive_classes else 0)
    
    # Assign human-readable binary class names
    df['binary_class'] = df['binary_label'].map({1: 'Malignant-Suspicious', 0: 'Non-malignant'})
    
    # Rename 'image' to 'image_id' as requested
    df = df.rename(columns={'image': 'image_id'})
    
    # 5. Extract only the required columns for our clean dataset
    final_cols = ['image_id', 'original_class', 'binary_label', 'binary_class']
    processed_df = df[final_cols].copy()
    
    # 6. Save the resulting processed dataset without modifying the original
    print(f"\nSaving processed dataset to: {output_path}")
    processed_df.to_csv(output_path, index=False)
    
    # 7. Print total records and class distributions
    total_records = len(processed_df)
    print(f"\nTotal records: {total_records}")
    
    print("\n--- Original Class Distribution ---")
    orig_counts = processed_df['original_class'].value_counts()
    for cls in classes:
        count = orig_counts.get(cls, 0)
        percentage = (count / total_records) * 100
        print(f"{cls}: {count} ({percentage:.2f}%)")
        
    print("\n--- Binary Class Distribution ---")
    bin_counts = processed_df['binary_class'].value_counts()
    for bin_cls in ['Malignant-Suspicious', 'Non-malignant']:
        count = bin_counts.get(bin_cls, 0)
        # Handle label mapped to string logic dynamically
        label = 1 if bin_cls == 'Malignant-Suspicious' else 0
        percentage = (count / total_records) * 100
        print(f"{bin_cls} (Label {label}): {count} ({percentage:.2f}%)")

    # 8. Verify the processed dataset meets all constraints
    print("\n--- Verifying Processed Dataset ---")
    
    # Check total records
    assert len(processed_df) == 10015, f"Expected 10015 records, found {len(processed_df)}"
    print("✓ Exactly 10,015 records verified.")
    
    # Check duplicates
    duplicate_ids = processed_df.duplicated(subset=['image_id']).sum()
    assert duplicate_ids == 0, f"Found {duplicate_ids} duplicate image IDs!"
    print("✓ No duplicate image IDs verified.")
    
    # Check missing binary labels
    missing_labels = processed_df['binary_label'].isnull().sum()
    assert missing_labels == 0, f"Found {missing_labels} missing binary labels!"
    print("✓ No missing binary labels verified.")
    
    # Check valid binary labels (only 0 and 1)
    invalid_labels = processed_df[~processed_df['binary_label'].isin([0, 1])]
    assert len(invalid_labels) == 0, "Found labels other than 0 and 1!"
    print("✓ Only 0 and 1 occur in binary_label verified.")
    
    # Check corresponding JPG existence
    # Read files with .jpg extension from raw/images folder
    jpg_files = list(images_dir.glob("*.jpg"))
    jpg_filenames = {f.stem for f in jpg_files}
    
    csv_image_ids = set(processed_df['image_id'])
    missing_images = csv_image_ids - jpg_filenames
    
    assert len(missing_images) == 0, f"Found {len(missing_images)} missing JPG files for IDs in dataset!"
    print(f"✓ All {len(csv_image_ids)} image_ids have a corresponding JPG file in data/raw/images.")

    print("\nDataset generation and verification completed successfully!")

if __name__ == '__main__':
    main()
