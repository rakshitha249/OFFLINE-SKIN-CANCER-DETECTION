import os
import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image
from torchvision import transforms
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

from model import create_model

# =================================================================================
# BEGINNER-FRIENDLY EDUCATIONAL NOTES: GRAD-CAM
# =================================================================================
# 1. What is Grad-CAM?
#    Grad-CAM stands for Gradient-weighted Class Activation Mapping. 
#    It is an explainability technique that produces a visual "heatmap" 
#    highlighting the important regions in an image that led the model to its decision.
#
# 2. Why is it useful?
#    Neural networks are often considered "black boxes" because they don't explicitly
#    tell us *why* they made a prediction. Grad-CAM helps us peek inside the box 
#    to verify if the model is looking at the actual skin lesion or just getting 
#    distracted by background noise (like a ruler, hair, or shadows).
#
# 3. Feature Maps and Gradients:
#    - Feature Maps: The outputs of the final convolutional layer. They contain 
#      high-level visual concepts (like shapes and textures).
#    - Gradients: The "learning signals" flowing backward from the prediction 
#      to the feature maps. By multiplying the feature maps by these gradients, 
#      we calculate the "importance" of each spatial location for the specific class.
#
# 4. The Heatmap:
#    Red/Yellow regions indicate high importance (the model focused heavily here).
#    Blue regions indicate low importance.
#
# 5. WARNING: Explanation vs. Proof
#    Grad-CAM explains *model behavior*, not biological reality. It tells us 
#    what pixels the model used mathematically. It does NOT prove the lesion 
#    is biologically malignant or benign. A model can make the right prediction 
#    for the wrong reason (e.g., looking at a surgical mark instead of the tumor).
#    Always consult a medical professional for actual diagnosis.
# =================================================================================

# Directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = DATA_DIR / "raw" / "images"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

TEST_CSV = PROCESSED_DIR / "test.csv"
BEST_FINETUNED_MODEL_PATH = MODELS_DIR / "best_finetuned_model.pth"
GRADCAM_OUTPUT_PNG = REPORTS_DIR / "gradcam_example.png"

def main():
    # 1. Device Configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # 2. Load Model
    if not BEST_FINETUNED_MODEL_PATH.exists():
        print(f"Error: Fine-tuned model checkpoint not found at {BEST_FINETUNED_MODEL_PATH}")
        return

    model = create_model()
    checkpoint = torch.load(BEST_FINETUNED_MODEL_PATH, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    print("✓ Successfully loaded fine-tuned model checkpoint.")

    # 3. Select an Image from Test Set
    test_df = pd.read_csv(TEST_CSV)
    
    # We will pick the first positive (malignant) sample from the test set for a good demonstration
    # If there are no positive samples, we fallback to the very first image.
    positive_samples = test_df[test_df['binary_label'] == 1]
    if not positive_samples.empty:
        sample_row = positive_samples.iloc[0]
    else:
        sample_row = test_df.iloc[0]
        
    image_id = sample_row['image_id']
    true_label = int(sample_row['binary_label'])
    
    image_path = IMAGES_DIR / f"{image_id}.jpg"
    
    if not image_path.exists():
        print(f"Error: Image {image_path} not found.")
        return

    # 4. Preprocess Image
    # A. Preprocessing for the PyTorch Model (Tensors + Normalization)
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    pil_img = Image.open(image_path).convert('RGB')
    input_tensor = test_transform(pil_img).unsqueeze(0).to(device)
    input_tensor.requires_grad_(True)
    
    # B. Preprocessing for the visualization overlay (Float [0, 1] numpy array, No Normalization)
    vis_img = pil_img.resize((224, 224))
    vis_img_np = np.array(vis_img, dtype=np.float32) / 255.0

    # 5. Model Prediction (Without torch.no_grad!)
    model_output = model(input_tensor)
    
    print("Model output shape:", model_output.shape)
    print("Model output requires_grad:", model_output.requires_grad)
    print("Model output:", model_output.detach().cpu())
    
    # Safely compute probabilities for display
    with torch.no_grad():
        prob = torch.sigmoid(model_output.squeeze()).item()
        pred_label = 1 if prob >= 0.5 else 0

    # 6. Grad-CAM Setup
    target_layer = model.features[-1][0]
    target_layers = [target_layer]
    
    # Custom target for a single binary logit model which outputs shape [B, 1]
    class BinaryLogitTarget:
        def __call__(self, model_output):
            return model_output.reshape(-1)[0]

    targets = [BinaryLogitTarget()]

    # Initialize Grad-CAM
    cam = GradCAM(model=model, target_layers=target_layers)

    print("Input requires_grad:", input_tensor.requires_grad)
    print("Model output requires_grad:", model_output.requires_grad)
    print("Target layer:", target_layer)

    # 7. Generate Heatmap
    # MUST run with gradients enabled so Grad-CAM can compute the backward pass
    with torch.enable_grad():
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
    
    # In this case, batch size is 1, so we take the first image's cam
    grayscale_cam = grayscale_cam[0, :]

    # Overlay on original image
    cam_image = show_cam_on_image(vis_img_np, grayscale_cam, use_rgb=True)

    # 8. Plot and Save
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    
    ax[0].imshow(vis_img_np)
    ax[0].set_title(f"Original Image\nTrue: {true_label}")
    ax[0].axis('off')
    
    ax[1].imshow(cam_image)
    ax[1].set_title(f"Grad-CAM\nPred: {pred_label} (Prob: {prob:.4f})")
    ax[1].axis('off')
    
    plt.tight_layout()
    plt.savefig(GRADCAM_OUTPUT_PNG)
    plt.close()

    # 9. Print Output Results
    print("\n=== Grad-CAM Execution Complete ===")
    print(f"Selected Image ID: {image_id}")
    print(f"True Label:        {true_label}")
    print(f"Predicted Label:   {pred_label}")
    print(f"Probability:       {prob:.4f}")
    print("✓ Grad-CAM generated successfully")
    print(f"✓ Saved visualization to {GRADCAM_OUTPUT_PNG}")
    print("===================================")


if __name__ == "__main__":
    main()
