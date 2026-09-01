import torch
import torch.nn as nn
from torchvision import models

# =================================================================================
# IMPORTANT EDUCATIONAL NOTES ON TRANSFER LEARNING
# =================================================================================
# 1. Transfer Learning & Pretrained Weights:
#    Instead of training a neural network from scratch (which takes weeks and huge
#    amounts of data), we take a model that has already been trained on millions of 
#    general images (ImageNet). This model has learned to recognize edges, shapes, 
#    and textures. These learned patterns are saved as "pretrained weights".
#
# 2. Backbone / Feature Extractor:
#    The main body of the network is called the backbone or feature extractor. 
#    Its job is to look at an image and extract useful visual patterns. We often 
#    "freeze" these layers initially so we don't destroy these valuable learned 
#    features while training on our small medical dataset.
#
# 3. Classifier:
#    The final layer of the network is the classifier. We replace the original 
#    1000-class ImageNet classifier with a new, randomly initialized 1-class 
#    classifier (Malignant vs Non-malignant). We only train this new classifier 
#    first.
#
# 4. Logits and Sigmoid:
#    The raw output of our final linear layer is a number from -infinity to +infinity 
#    called a "logit". We do NOT apply the Sigmoid function (which squishes the number 
#    between 0 and 1) inside the model. Why? Because PyTorch's loss function 
#    (BCEWithLogitsLoss) combines the Sigmoid and the Loss calculation into one 
#    mathematically optimized and numerically stable step.
# =================================================================================

def create_model():
    """
    Creates an EfficientNet-B0 model pretrained on ImageNet, modifies it for 
    binary classification, and freezes the backbone.
    """
    # Load the pretrained EfficientNet-B0
    # weights='DEFAULT' loads the best available ImageNet weights for our torchvision version
    model = models.efficientnet_b0(weights='DEFAULT')
    
    # Freeze the feature extractor (backbone)
    # We set requires_grad = False so these weights are not updated during the first phase of training
    for param in model.features.parameters():
        param.requires_grad = False
        
    # EfficientNet-B0's classifier takes 1280 features from the backbone
    num_ftrs = model.classifier[1].in_features
    
    # Replace the final classifier
    # We output 1 logit (binary classification) instead of 1000 (ImageNet)
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(num_ftrs, 1)
    )
    
    return model

def unfreeze_last_layers(model):
    """
    Unfreezes the last few layers of the feature extractor for fine-tuning.
    This allows the model to adapt its deeper visual features specifically to skin lesions
    after the newly initialized classifier has converged a bit.
    """
    # Unfreeze the last two blocks of the EfficientNet features
    # features[-1] is the final Conv2dNormActivation block
    # features[-2] is the final MBConv block
    for param in model.features[-1].parameters():
        param.requires_grad = True
        
    for param in model.features[-2].parameters():
        param.requires_grad = True
        
    print("Unfroze the final layers of the backbone for fine-tuning.")

def count_parameters(model):
    """
    Calculates and prints the total and trainable parameters in the model.
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    
    return total_params, trainable_params

if __name__ == "__main__":
    print("Testing Model Architecture...")
    
    # 1. Create the model
    model = create_model()
    
    # 2. Print the final classifier to verify the change
    print("\n--- Final Classifier Architecture ---")
    print(model.classifier)
    
    # 3. Print parameters
    print("\n--- Parameter Count (Initial State) ---")
    count_parameters(model)
    
    # 4. Test a forward pass with a dummy tensor
    # Shape: [Batch Size, Channels, Height, Width]
    dummy_input = torch.randn(2, 3, 224, 224)
    print("\n--- Forward Pass Test ---")
    print(f"Input shape: {dummy_input.shape}")
    
    # Perform forward pass
    output = model(dummy_input)
    
    print(f"Output shape: {output.shape}")
    print(f"Expected shape: torch.Size([2, 1])")
    
    # 5. Verify the shape
    if output.shape == torch.Size([2, 1]):
        print("✓ Forward pass successful and output shape is correct!")
    else:
        print("✗ Output shape is incorrect.")
