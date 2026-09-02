import streamlit as st
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# Set the page configuration for a professional look
st.set_page_config(
    page_title="Offline Skin Lesion Analyzer",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# MODEL LOADING (CACHED)
# -----------------------------------------------------------------------------
# We use st.cache_resource so the model is only loaded once and not reloaded 
# every time the user interacts with the UI.
@st.cache_resource
def load_model():
    # Automatically use CUDA if available, otherwise CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Recreate the exact EfficientNet-B0 architecture
    # weights=None ensures we don't attempt to download ImageNet weights (Offline mode)
    model = models.efficientnet_b0(weights=None)
    
    # EfficientNet-B0's classifier takes 1280 features from the backbone
    num_ftrs = model.classifier[1].in_features
    
    # Replace the final classifier for binary classification (1 output logit)
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(num_ftrs, 1)
    )
    
    # Load the trained checkpoint
    checkpoint_path = "models/best_finetuned_model.pth"
    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False
    )

    model.load_state_dict(checkpoint["model_state_dict"])
    
    # Set model to evaluation mode (disables dropout, batchnorm updates, etc.)
    model.eval()
    
    # Move model to the selected device
    model = model.to(device)
    
    return model, device

# Load the model and get the device
model, device = load_model()

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
# Add model information to the sidebar
st.sidebar.header("Model Information")

# Display the device dynamically (CPU or CUDA)
st.sidebar.markdown(f"""
- **Model:** EfficientNet-B0
- **Task:** Binary skin lesion classification
- **Inference:** Local / Offline
- **Device:** {device.type.upper()}
""")

# -----------------------------------------------------------------------------
# MAIN CONTENT AREA
# -----------------------------------------------------------------------------
# Clean professional title
st.title("Offline Skin Lesion Analyzer")

# Short description of the application
st.write(
    "AI-assisted skin lesion image analysis using a locally running EfficientNet-B0 model."
)

# Prominent medical disclaimer using Streamlit's warning box
st.warning(
    "**Disclaimer:** This application is an educational/research prototype and is "
    "**NOT** a medical diagnostic tool. Predictions should not be used to diagnose "
    "or treat skin cancer."
)

st.markdown("---")

# -----------------------------------------------------------------------------
# IMAGE PREPROCESSING
# -----------------------------------------------------------------------------
# Exact preprocessing used during validation/test evaluation
# No random augmentations are used here
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# -----------------------------------------------------------------------------
# IMAGE UPLOADER
# -----------------------------------------------------------------------------
st.subheader("Upload Image")
# Create a file uploader that accepts JPG, JPEG, and PNG image formats
uploaded_file = st.file_uploader(
    "Choose a skin lesion image...", 
    type=["jpg", "jpeg", "png"]
)

# -----------------------------------------------------------------------------
# IMAGE DISPLAY & ANALYSIS
# -----------------------------------------------------------------------------
# If a file has been uploaded by the user
if uploaded_file is not None:
    try:
        # Open the uploaded image using PIL
        image = Image.open(uploaded_file)
        
        # Display the uploaded image
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        st.markdown("---")
        
        # Add a prominent "Analyze Image" button
        if st.button("Analyze Image", type="primary"):
            # Display a spinner while processing
            with st.spinner("Analyzing image..."):
                # 1. Preprocessing: ensure image is RGB
                img_rgb = image.convert('RGB')
                
                # 2. Apply transformations (resize, to tensor, normalize)
                # Add a batch dimension using unsqueeze (shape becomes [1, 3, 224, 224])
                input_tensor = preprocess(img_rgb).unsqueeze(0).to(device)
                # Enable gradients on the input tensor for Grad-CAM
                input_tensor.requires_grad_(True)
                
                # 3. Perform local inference
                # We do NOT use torch.no_grad() because Grad-CAM requires gradients to compute the backward pass
                with torch.enable_grad():
                    output_logit = model(input_tensor)
                    
                    # 4. Convert the model's single binary output (logit) into a probability using sigmoid
                    probability = torch.sigmoid(output_logit).item()
                
                # 5. Apply threshold
                threshold = 0.5
                predicted_label = 1 if probability >= threshold else 0
                
                # 6. Determine display text based on our convention
                # Label 0 = Non-malignant, Label 1 = Malignant-Suspicious
                if predicted_label == 1:
                    prediction_text = "Malignant-Suspicious"
                    interpretation = "The model assigned a higher probability to the malignant/suspicious class."
                    color = "red"
                else:
                    prediction_text = "Non-malignant"
                    interpretation = "The model assigned a lower probability to the malignant/suspicious class."
                    color = "green"
                
                # Display Results
                st.subheader("Analysis Results")
                
                st.markdown(f"**Prediction:** <span style='color:{color}; font-size: 20px;'>{prediction_text}</span>", unsafe_allow_html=True)
                
                # Format probabilities as percentages
                prob_percentage = probability * 100
                non_malignant_percentage = 100.0 - prob_percentage
                
                st.subheader("Model Output")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Malignant-Suspicious",
                        f"{prob_percentage:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Non-malignant",
                        f"{non_malignant_percentage:.1f}%"
                    )
                
                st.markdown("**Prediction probability**")
                st.progress(float(probability))
                
                st.caption(
                    "*(Note: This probability is a statistical model output, "
                    "not a measure of medical certainty.)*"
                )
                
                st.info(interpretation)
                
                # Display the visible disclaimer again near the result
                st.caption("*This result is generated by an AI research prototype and is not a medical diagnosis.*")
                
                st.markdown("---")
                
                # -----------------------------------------------------------------------------
                # UNCERTAINTY ASSESSMENT
                # -----------------------------------------------------------------------------
                st.subheader("Uncertainty Assessment")
                
                probability_margin = abs(probability - 0.5)
                margin_percentage = probability_margin * 100
                
                if probability_margin < 0.10:
                    conf_interpretation = "Low confidence / uncertain prediction"
                    conf_explanation = "The model probabilities are relatively close to each other, indicating low separation between the two classes."
                    msg = (f"**Model confidence:** {conf_interpretation}\n\n"
                           f"**Prediction separation:** {margin_percentage:.1f} percentage points\n\n"
                           f"{conf_explanation}\n\n"
                           "⚠ Uncertain prediction: the model probabilities are relatively close. This result should be interpreted cautiously.")
                    st.warning(msg)
                elif probability_margin < 0.25:
                    conf_interpretation = "Moderate confidence"
                    conf_explanation = "The model shows a moderate preference toward the predicted class."
                    msg = (f"**Model confidence:** {conf_interpretation}\n\n"
                           f"**Prediction separation:** {margin_percentage:.1f} percentage points\n\n"
                           f"{conf_explanation}")
                    st.info(msg)
                else:
                    conf_interpretation = "Higher model confidence"
                    conf_explanation = "The model shows a stronger preference toward the predicted class."
                    msg = (f"**Model confidence:** {conf_interpretation}\n\n"
                           f"**Prediction separation:** {margin_percentage:.1f} percentage points\n\n"
                           f"{conf_explanation}")
                    st.success(msg)

                st.markdown("---")
                
                # -----------------------------------------------------------------------------
                # GRAD-CAM EXPLAINABILITY
                # -----------------------------------------------------------------------------
                st.subheader("Explainability (Grad-CAM)")
                
                # Preprocessing for the visualization overlay (Float [0, 1] numpy array)
                vis_img = img_rgb.resize((224, 224))
                vis_img_np = np.array(vis_img, dtype=np.float32) / 255.0
                
                # Target layer configuration for EfficientNet-B0
                target_layer = model.features[-1][0]
                target_layers = [target_layer]
                
                # Custom target for a single binary logit model
                class BinaryLogitTarget:
                    def __call__(self, model_output):
                        return model_output.reshape(-1)[0]
                
                targets = [BinaryLogitTarget()]
                
                # Initialize Grad-CAM
                cam = GradCAM(model=model, target_layers=target_layers)
                
                # Generate heatmap
                with torch.enable_grad():
                    grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
                
                grayscale_cam = grayscale_cam[0, :]
                cam_image = show_cam_on_image(vis_img_np, grayscale_cam, use_rgb=True)
                
                # Display Grad-CAM image
                st.image(cam_image, caption="Grad-CAM Heatmap", use_container_width=True)
                st.caption("Red/Yellow regions indicate areas the model focused on heavily to make its prediction.")

    except Exception as e:
        # Handle invalid/corrupted images gracefully
        st.error(f"Error processing the uploaded image. Please ensure it is a valid image file. Details: {e}")
