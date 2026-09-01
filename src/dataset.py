import pandas as pd
from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

# =================================================================================
# IMPORTANT EDUCATIONAL NOTES ON DATASET AND DATALOADER
# =================================================================================
# 1. What does a 'Dataset' do?
#    The PyTorch Dataset class is responsible for loading a SINGLE piece of data 
#    and its corresponding label. It handles the logic of reading from the disk, 
#    opening the image, applying transformations, and returning an (image, label) pair.
#
# 2. What does a 'DataLoader' do?
#    The DataLoader wraps the Dataset and provides an iterable over it. It handles
#    batching (grouping multiple images together), shuffling, and parallel data loading 
#    (using multiple workers/CPU cores) to feed data efficiently to the model during training.
# =================================================================================

class SkinLesionDataset(Dataset):
    def __init__(self, csv_file, images_dir, transform=None):
        """
        Args:
            csv_file (Path or str): Path to the csv file with annotations.
            images_dir (Path or str): Directory with all the images.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.data_frame = pd.read_csv(csv_file)
        self.images_dir = Path(images_dir)
        self.transform = transform

    def __len__(self):
        # Returns the total number of samples in the dataset
        return len(self.data_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        # Obtain image_id and construct the full path
        image_id = self.data_frame.iloc[idx]['image_id']
        image_path = self.images_dir / f"{image_id}.jpg"

        # Load image using PIL and ensure it's in RGB format
        image = Image.open(image_path).convert('RGB')

        # Obtain the binary label
        label = int(self.data_frame.iloc[idx]['binary_label'])

        # Apply transformations if provided
        if self.transform:
            image = self.transform(image)

        # PyTorch expects labels as tensors
        label = torch.tensor(label, dtype=torch.float32)

        return image, label

def create_dataloaders(project_root=None):
    """
    Creates and returns the train, validation, and test dataloaders.
    """
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent
        
    data_dir = project_root / "data"
    processed_dir = data_dir / "processed"
    images_dir = data_dir / "raw" / "images"

    train_csv = processed_dir / "train.csv"
    val_csv = processed_dir / "val.csv"
    test_csv = processed_dir / "test.csv"

    # =================================================================================
    # IMPORTANT EDUCATIONAL NOTES ON TRANSFORMS
    # =================================================================================
    # 1. Why use training augmentation?
    #    Data augmentation creates modified versions of our training images (e.g., 
    #    flipped or rotated). This prevents the model from memorizing exact pixel values
    #    and helps it generalize better to unseen variations of skin lesions.
    #
    # 2. Why NO random augmentation for Validation/Test?
    #    Validation and Test sets are meant to evaluate how well the model performs 
    #    on real, unmodified data. Adding randomness here would make our evaluation 
    #    inconsistent and noisy.
    #
    # 3. Why ImageNet normalization?
    #    Most pre-trained models (like ResNet) were originally trained on the ImageNet 
    #    dataset. To use them effectively via Transfer Learning, our input images must 
    #    have the same statistical distribution (mean and standard deviation) that the 
    #    model originally learned.
    # =================================================================================

    # Training transforms with augmentation
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Validation and test transforms (Resize, ToTensor, Normalize only)
    val_test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Create dataset instances
    train_dataset = SkinLesionDataset(csv_file=train_csv, images_dir=images_dir, transform=train_transform)
    val_dataset = SkinLesionDataset(csv_file=val_csv, images_dir=images_dir, transform=val_test_transform)
    test_dataset = SkinLesionDataset(csv_file=test_csv, images_dir=images_dir, transform=val_test_transform)

    # Create DataLoaders
    # Note: batch_size=16 initially (project is currently on CPU)
    # num_workers=0 initially for Windows compatibility
    # shuffle=True only for training dataset to ensure random batches
    batch_size = 16
    num_workers = 0

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return train_loader, val_loader, test_loader

if __name__ == "__main__":
    print("Testing Dataset and DataLoaders...")
    
    # Create the dataloaders
    train_loader, val_loader, test_loader = create_dataloaders()
    
    # Retrieve one training batch
    images, labels = next(iter(train_loader))
    
    # Print tests
    print("\n--- DataLoader Test Results ---")
    print(f"Batch size: {images.size(0)}")
    print(f"Image tensor shape (Batch, Channels, Height, Width): {images.shape}")
    print(f"Label tensor shape: {labels.shape}")
    print(f"First few labels in batch: {labels[:5].tolist()}")
    
    print("\n✓ Dataset and DataLoader successfully implemented and tested!")
