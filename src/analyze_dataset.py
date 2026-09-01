import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

def main():
    # Define paths relative to the current file's location (the project root)
    # __file__ is the script path, parent is src/, parent.parent is project root
    project_root = Path(__file__).resolve().parent.parent
    
    data_dir = project_root / "data" / "raw"
    images_dir = data_dir / "images"
    csv_path = data_dir / "ISIC2018_Task3_Training_GroundTruth.csv"
    reports_dir = project_root / "reports"
    
    # Ensure the reports directory exists to save our plot
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load the ground-truth CSV
    print(f"Loading dataset from: {csv_path}")
    # pandas is a powerful data manipulation library, read_csv loads the file into a DataFrame
    df = pd.read_csv(csv_path)
    
    # 2. Basic dataset inspection
    print("\n--- Basic Dataset Information ---")
    print(f"CSV Shape (rows, columns): {df.shape}")
    print(f"Column Names: {list(df.columns)}")
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Check the number of unique image IDs
    num_unique_ids = df['image'].nunique()
    print(f"\nNumber of unique image IDs: {num_unique_ids}")
    
    # 3 & 4. Determine diagnosis/class and calculate distribution
    # The ISIC dataset uses a one-hot encoding style format for its 7 classes
    classes = ['MEL', 'NV', 'BCC', 'AKIEC', 'BKL', 'DF', 'VASC']
    
    # We can determine the dominant class by finding the column with the maximum value (1.0)
    # and creating a new 'diagnosis' column for easier analysis
    df['diagnosis'] = df[classes].idxmax(axis=1)
    
    print("\n--- Class Distribution ---")
    class_counts = df['diagnosis'].value_counts()
    total_images = len(df)
    
    # Print the count and percentage for each of the 7 original ISIC classes
    for cls in classes:
        count = class_counts.get(cls, 0)
        percentage = (count / total_images) * 100
        print(f"{cls}: {count} images ({percentage:.2f}%)")
        
    # 5. Image File Verification
    print("\n--- Image File Verification ---")
    # Find all .jpg files in the images directory using pathlib's glob
    jpg_files = list(images_dir.glob("*.jpg"))
    # Extract just the filenames (without the .jpg extension) to match with the CSV
    jpg_filenames = [f.stem for f in jpg_files]
    
    print(f"Found {len(jpg_files)} JPG files in {images_dir}")
    
    # Convert lists to sets for efficient comparison
    csv_image_ids = set(df['image'])
    folder_image_ids = set(jpg_filenames)
    
    # Find IDs in the CSV that don't have a corresponding image file
    missing_in_folder = csv_image_ids - folder_image_ids
    # Find image files that aren't listed in the CSV
    missing_in_csv = folder_image_ids - csv_image_ids
    
    if missing_in_folder:
        print(f"\nWARNING: Missing {len(missing_in_folder)} images (in CSV but no JPG file found).")
        print(f"Examples: {list(missing_in_folder)[:5]}")
    else:
        print("\nSUCCESS: All image IDs in the CSV have a corresponding JPG file.")
        
    if missing_in_csv:
        print(f"WARNING: Found {len(missing_in_csv)} JPG files that are not in the CSV.")
        print(f"Examples: {list(missing_in_csv)[:5]}")
    else:
        print("SUCCESS: All JPG files have a corresponding record in the CSV.")
        
    # 6. Check for duplicate IDs and missing values
    print("\n--- Data Quality Checks ---")
    duplicate_ids = df.duplicated(subset=['image']).sum()
    print(f"Duplicate image IDs in CSV: {duplicate_ids}")
    
    # Check if there are any NaN (Not a Number) or missing values across the entire DataFrame
    missing_values = df.isnull().sum().sum()
    print(f"Total missing values in CSV: {missing_values}")
    
    # 7. Create a class distribution visualization using matplotlib
    print("\n--- Generating Visualization ---")
    plt.figure(figsize=(10, 6)) # Set the size of the figure
    
    # Create a bar plot of the class counts
    class_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    
    # Add titles and labels to make the chart readable
    plt.title('ISIC 2018 Task 3 - Class Distribution')
    plt.xlabel('Diagnosis Class')
    plt.ylabel('Number of Images')
    
    # Rotate the x-axis labels so they don't overlap
    plt.xticks(rotation=45)
    
    # Add horizontal gridlines for easier reading
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout() # Adjust layout so everything fits nicely
    
    # Save the plot to the reports directory
    viz_path = reports_dir / 'class_distribution.png'
    plt.savefig(viz_path)
    print(f"Saved class distribution visualization to: {viz_path}")

if __name__ == '__main__':
    main()
