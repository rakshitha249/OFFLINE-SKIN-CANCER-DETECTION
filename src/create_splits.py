import pandas as pd
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit

def main():
    # Define paths relative to the current file's location
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"
    processed_data_dir = project_root / "data" / "processed"
    
    binary_csv_path = processed_data_dir / "binary_dataset.csv"
    lesion_csv_path = raw_data_dir / "ISIC2018_Task3_Training_LesionGroupings.csv"
    
    train_out_path = processed_data_dir / "train.csv"
    val_out_path = processed_data_dir / "val.csv"
    test_out_path = processed_data_dir / "test.csv"
    
    # 1-2. Load data
    print(f"Loading datasets...")
    binary_df = pd.read_csv(binary_csv_path)
    lesion_df = pd.read_csv(lesion_csv_path)
    
    # 3. Merge datasets
    # We join binary_dataset.image_id with lesion_groupings.image
    df = pd.merge(binary_df, lesion_df, left_on='image_id', right_on='image', how='inner')
    
    # 4. Verify merge ensures exactly one lesion_id per image
    assert len(df) == len(binary_df), "Merge lost or duplicated rows!"
    assert df['lesion_id'].isnull().sum() == 0, "Some images are missing a lesion_id after merge!"
    
    # Clean up the redundant duplicate 'image' column from the merge
    if 'image' in df.columns:
        df = df.drop(columns=['image'])
        
    # =================================================================================
    # IMPORTANT EDUCATIONAL NOTES ON SPLITTING & DATA LEAKAGE
    # =================================================================================
    # 1. What is Data Leakage?
    #    Data Leakage occurs when the model sees information during training that it 
    #    shouldn't, causing it to "cheat." If the model memorizes a specific lesion's 
    #    visual background (like a unique hair or lighting) in the training set and 
    #    that same lesion appears in the test set, it artificially boosts our accuracy 
    #    metrics without actually learning to detect cancer.
    #
    # 2. Why must a lesion_id stay within one split?
    #    To prevent data leakage. All images of the same physical lesion must stay 
    #    grouped together in either train, val, or test. They cannot span across sets.
    #
    # 3. Why must the test set remain isolated?
    #    The test set represents strictly unseen "real-world" data. It is only used 
    #    at the very end of our project to evaluate the final model. We tune the 
    #    model's hyperparameters using the validation set, NEVER the test set.
    #
    # 4. Why use random_state=42?
    #    Setting a fixed seed ensures our random split is exactly reproducible. 
    #    Anyone running this script will get the exact same images in the exact same 
    #    train, val, and test sets, making our research verifiable.
    # =================================================================================

    # 5-10. Perform Group-Aware Splitting
    # We want an approximate 70% Train, 15% Val, 15% Test split by group.
    # We'll use sklearn's GroupShuffleSplit twice to achieve this.
    
    # First split: Separate out 30% of the groups for Temp (Val + Test)
    # The remaining 70% goes to Training.
    gss1 = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=42)
    train_idx, temp_idx = next(gss1.split(df, groups=df['lesion_id']))
    
    train_df = df.iloc[train_idx].copy()
    temp_df = df.iloc[temp_idx].copy()
    
    # Second split: Split the Temp dataset evenly (50/50) into Validation and Test
    # 50% of 30% = 15% each.
    gss2 = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=42)
    val_idx, test_idx = next(gss2.split(temp_df, groups=temp_df['lesion_id']))
    
    val_df = temp_df.iloc[val_idx].copy()
    test_df = temp_df.iloc[test_idx].copy()
    
    # 11-12. Save datasets with required columns
    cols_to_keep = ['image_id', 'original_class', 'binary_label', 'binary_class', 'lesion_id']
    train_df = train_df[cols_to_keep]
    val_df = val_df[cols_to_keep]
    test_df = test_df[cols_to_keep]
    
    train_df.to_csv(train_out_path, index=False)
    val_df.to_csv(val_out_path, index=False)
    test_df.to_csv(test_out_path, index=False)
    
    # 13. Print detailed summary
    def print_split_summary(name, split_df):
        total_imgs = len(split_df)
        total_groups = split_df['lesion_id'].nunique()
        count_0 = (split_df['binary_label'] == 0).sum()
        count_1 = (split_df['binary_label'] == 1).sum()
        pct_0 = count_0 / total_imgs * 100 if total_imgs > 0 else 0
        pct_1 = count_1 / total_imgs * 100 if total_imgs > 0 else 0
        
        print(f"\n{name}:")
        print(f"- image count: {total_imgs}")
        print(f"- lesion-group count: {total_groups}")
        print(f"- binary label 0 count and percentage: {count_0} ({pct_0:.2f}%)")
        print(f"- binary label 1 count and percentage: {count_1} ({pct_1:.2f}%)")
        
    print("\n--- Split Summary ---")
    print(f"Total images: {len(df)}")
    print(f"Total lesion groups: {df['lesion_id'].nunique()}")
    
    print_split_summary("TRAIN", train_df)
    print_split_summary("VALIDATION", val_df)
    print_split_summary("TEST", test_df)
    
    # 14-15. Verifications
    print("\n--- Verifying Splits ---")
    
    all_imgs = pd.concat([train_df, val_df, test_df])
    
    # Verification Logic
    no_dup_imgs = not train_df['image_id'].duplicated().any() and \
                  not val_df['image_id'].duplicated().any() and \
                  not test_df['image_id'].duplicated().any()
                  
    total_unique_imgs = all_imgs['image_id'].nunique()
    total_imgs_count = len(all_imgs)
    
    train_groups = set(train_df['lesion_id'])
    val_groups = set(val_df['lesion_id'])
    test_groups = set(test_df['lesion_id'])
    
    overlap_train_val = train_groups.intersection(val_groups)
    overlap_train_test = train_groups.intersection(test_groups)
    overlap_val_test = val_groups.intersection(test_groups)
    
    missing_labels = all_imgs['binary_label'].isnull().sum()
    invalid_labels = len(all_imgs[~all_imgs['binary_label'].isin([0, 1])])
    
    # Print clear results
    print(f"✓ No duplicate image IDs within a split: {no_dup_imgs}")
    print(f"✓ No image appears in multiple splits: {total_unique_imgs == total_imgs_count}")
    print(f"✓ No lesion_id appears in multiple splits: {len(overlap_train_val) == 0 and len(overlap_train_test) == 0 and len(overlap_val_test) == 0}")
    print(f"✓ All 10,015 original images are represented exactly once: {total_imgs_count == 10015 and total_unique_imgs == 10015}")
    print(f"✓ No missing binary labels: {missing_labels == 0}")
    print(f"✓ Only labels 0 and 1 are present: {invalid_labels == 0}")
    
    # Strict assertions to halt execution if a rule is violated
    assert no_dup_imgs, "Duplicates found within splits!"
    assert total_unique_imgs == total_imgs_count, "An image is in multiple splits!"
    assert len(overlap_train_val) == 0, "Train and Val share lesion IDs!"
    assert len(overlap_train_test) == 0, "Train and Test share lesion IDs!"
    assert len(overlap_val_test) == 0, "Val and Test share lesion IDs!"
    assert total_imgs_count == 10015, f"Expected 10015 total images across splits, got {total_imgs_count}"
    assert missing_labels == 0, "Found missing labels!"
    assert invalid_labels == 0, "Found invalid labels!"
    
    print("\nData splits generated and successfully verified!")

if __name__ == "__main__":
    main()
