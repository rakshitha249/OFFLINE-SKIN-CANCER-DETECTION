import pandas as pd
from pathlib import Path

def main():
    # Define paths relative to the current file's location
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "raw" / "ISIC2018_Task3_Training_LesionGroupings.csv"
    
    print(f"Reading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # 2. Basic Inspection
    print("\n--- Basic Dataset Information ---")
    print(f"CSV Shape (rows, columns): {df.shape}")
    print(f"Column Names: {list(df.columns)}")
    print("\nFirst 10 rows:")
    print(df.head(10))
    
    # 3. Identify Columns
    # Typically in ISIC 2018, columns are 'image' and 'lesion_id'
    image_col = 'image' if 'image' in df.columns else df.columns[0]
    lesion_col = 'lesion_id' if 'lesion_id' in df.columns else df.columns[1]
    
    print(f"\n--- Column Identification ---")
    print(f"Image ID column: '{image_col}'")
    print(f"Lesion/Group ID column: '{lesion_col}'")
    
    # Check if there are any other columns that might represent diagnosis/type
    diagnosis_col = next((col for col in df.columns if col not in [image_col, lesion_col]), None)
    if diagnosis_col:
        print(f"Diagnosis/type column found: '{diagnosis_col}'")
    else:
        print("No additional diagnosis/type column found in this file.")
        
    print("\n--- Lesion Grouping Analysis ---")
    
    # =================================================================================
    # IMPORTANT EDUCATIONAL NOTE: WHAT IS LESION GROUPING AND DATA LEAKAGE?
    # =================================================================================
    # "Lesion grouping" indicates whether multiple images were taken of the exact 
    # same physical skin lesion (e.g., zoomed in, zoomed out, different angles).
    # 
    # Why it matters: Data Leakage!
    # If we randomly split our images into training and validation sets, we might end
    # up with Image A (of Lesion X) in the training set and Image B (also of Lesion X)
    # in the validation set. 
    #
    # The model might simply memorize the unique visual features of Lesion X (like skin 
    # texture, hair, or lighting) from Image A, and perfectly predict Image B without 
    # actually learning what cancer looks like. This causes the validation accuracy to 
    # look artificially high. 
    #
    # To fix this, we perform "Group-K-Fold" or "Group Shuffle Split". We group all 
    # images of the same lesion together and ensure the entire group goes strictly 
    # into either the training set OR the validation set, never both.
    # =================================================================================

    # 4 & 5. Check Group Sizes
    num_unique_images = df[image_col].nunique()
    num_unique_lesions = df[lesion_col].nunique()
    print(f"\nNumber of unique image IDs: {num_unique_images}")
    print(f"Number of unique lesion/group IDs: {num_unique_lesions}")
    
    # Group the dataframe by lesion_id and count how many images are in each group
    images_per_lesion = df.groupby(lesion_col)[image_col].count()
    
    # Calculate group sizes based on the counts
    groups_with_one_image = (images_per_lesion == 1).sum()
    groups_with_multiple_images = (images_per_lesion > 1).sum()
    max_images_in_group = images_per_lesion.max()
    
    print("\n--- Group Statistics ---")
    print(f"Number of groups containing exactly 1 image: {groups_with_one_image}")
    print(f"Number of groups containing more than 1 image: {groups_with_multiple_images}")
    print(f"Maximum number of images in a single group: {max_images_in_group}")
    
    # 6. Check for duplicates
    print("\n--- Duplicate Check ---")
    duplicate_image_ids = df.duplicated(subset=[image_col]).sum()
    print(f"Number of duplicate image IDs in CSV: {duplicate_image_ids}")
    if duplicate_image_ids == 0:
        print("✓ Each image ID appears on exactly one row.")
    else:
        print(f"⚠️ Warning: Found {duplicate_image_ids} duplicate image IDs!")

if __name__ == '__main__':
    main()
