import streamlit as st
from PIL import Image
import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
import os
import csv
from datetime import datetime


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
    
    checkpoint_path = "models/best_finetuned_model.pth"
    if not os.path.exists(checkpoint_path):
        return None, device
        
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

if model is None:
    st.error("Model checkpoint is missing. The application cannot perform predictions until the trained model is supplied at 'models/best_finetuned_model.pth'. This is a local/offline application.")
    st.stop()

# -----------------------------------------------------------------------------
# IMAGE QUALITY ASSESSMENT
# -----------------------------------------------------------------------------
def assess_image_quality(image):
    """
    Calculates basic image-quality indicators before analysis.
    Checks resolution, brightness, and sharpness.
    """
    # 1. RESOLUTION
    width, height = image.size
    if width < 224 or height < 224:
        resolution_status = "Low"
    elif width < 400 or height < 400:
        resolution_status = "Acceptable"
    else:
        resolution_status = "Good"
        
    # 2. BRIGHTNESS
    # Convert image to RGB then grayscale
    img_gray = image.convert('RGB').convert('L')
    img_gray_np = np.array(img_gray)
    mean_brightness = np.mean(img_gray_np)
    
    if mean_brightness < 40:
        brightness_status = "Very Dark"
    elif mean_brightness < 70:
        brightness_status = "Dark"
    elif mean_brightness < 191:
        brightness_status = "Normal"
    elif mean_brightness <= 220:
        brightness_status = "Bright"
    else:
        brightness_status = "Very Bright"
        
    # 3. SHARPNESS
    # Calculate horizontal and vertical pixel differences using np.diff
    diff_x = np.diff(img_gray_np, axis=1)
    diff_y = np.diff(img_gray_np, axis=0)
    sharpness = np.var(diff_x) + np.var(diff_y)
    
    if sharpness < 20:
        sharpness_status = "Very Blurry"
    elif sharpness < 50:
        sharpness_status = "Blurry"
    elif sharpness < 150:
        sharpness_status = "Acceptable"
    else:
        sharpness_status = "Good"
        
    # 4. OVERALL QUALITY
    problems = []
    if resolution_status == "Low":
        problems.append("Image resolution is low.")
    if brightness_status in ["Very Dark", "Very Bright"]:
        problems.append("Image brightness may affect analysis.")
    if sharpness_status in ["Very Blurry", "Blurry"]:
        problems.append("Image appears blurry.")
        
    if len(problems) == 0:
        overall_quality = "Good"
    elif len(problems) == 1:
        overall_quality = "Acceptable"
    else:
        overall_quality = "Needs Attention"
        
    return {
        "width": width,
        "height": height,
        "brightness": mean_brightness,
        "brightness_status": brightness_status,
        "sharpness": sharpness,
        "sharpness_status": sharpness_status,
        "resolution_status": resolution_status,
        "overall_quality": overall_quality,
        "problems": problems
    }

# -----------------------------------------------------------------------------
# PREDICTION HISTORY
# -----------------------------------------------------------------------------
def save_prediction_history(image_name, prediction, malignant_probability, non_malignant_probability, confidence, image_quality):
    """
    Saves the prediction results to a local CSV file.
    Creates the file and header if it doesn't exist.
    """
    history_dir = "history"
    history_file = os.path.join(history_dir, "prediction_history.csv")
    
    # Ensure directory exists just in case
    os.makedirs(history_dir, exist_ok=True)
    
    file_exists = os.path.isfile(history_file)
    
    with open(history_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if newly created
        if not file_exists:
            writer.writerow([
                "timestamp", 
                "image_name", 
                "prediction", 
                "malignant_probability", 
                "non_malignant_probability", 
                "confidence", 
                "image_quality"
            ])
            
        # Write the new row
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([
            timestamp,
            image_name,
            prediction,
            malignant_probability,
            non_malignant_probability,
            confidence,
            image_quality
        ])

def load_prediction_history():
    """
    Loads prediction history from the local CSV file.
    Returns a list of dictionaries, or an empty list if no history exists.
    """
    history_file = os.path.join("history", "prediction_history.csv")
    if not os.path.isfile(history_file) or os.path.getsize(history_file) == 0:
        return []
        
    records = []
    try:
        with open(history_file, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    except Exception:
        pass
    return records

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
    "**Disclaimer:** This project is an AI research and educational prototype. "
    "Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. "
    "The system is not a medical diagnostic device and should not be used to make clinical decisions."
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
        
        # -----------------------------------------------------------------------------
        # IMAGE QUALITY ASSESSMENT DISPLAY
        # -----------------------------------------------------------------------------
        quality_data = assess_image_quality(image)
        
        st.subheader("Image Quality Assessment")
        st.caption("This assessment describes properties of the uploaded image and does not validate the model prediction.")
        
        with st.container():
            st.markdown(f"**Overall image quality: {quality_data['overall_quality']}**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Resolution**")
                st.write(f"{quality_data['width']} × {quality_data['height']}")
                st.caption(quality_data['resolution_status'])
            with col2:
                st.markdown("**Brightness**")
                st.write(f"{quality_data['brightness']:.1f}")
                st.caption(quality_data['brightness_status'])
            with col3:
                st.markdown("**Sharpness**")
                st.write(f"{quality_data['sharpness']:.1f}")
                st.caption(quality_data['sharpness_status'])
            
            if quality_data["overall_quality"] == "Good":
                st.info("The image characteristics are within the preferred range.")
            else:
                warn_msg = "Prediction is still generated, but the image-quality assessment indicates that the uploaded image has characteristics outside the preferred range:\n"
                for prob in quality_data["problems"]:
                    warn_msg += f"- {prob}\n"
                st.warning(warn_msg)
                
            st.caption("Image quality assessment is separate from the model prediction and does not indicate whether the prediction is correct.")
        
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
                else:
                    prediction_text = "Non-malignant"
                
                # -----------------------------------------------------------------------------
                # ANALYSIS RESULTS HIERARCHY
                # -----------------------------------------------------------------------------
                st.subheader("Analysis Results")
                
                with st.container():
                    # A. Model Prediction
                    st.markdown("### A. Model prediction")
                    st.markdown(f"<span style='font-size: 24px; font-weight: bold;'>{prediction_text}</span>", unsafe_allow_html=True)
                    st.caption("Based on the established decision threshold applied to the model's output probability.")
                    
                    st.markdown("---")
                    
                    # B. Estimated model probability
                    st.markdown("### B. Estimated model probability")
                    prob_percentage = probability * 100
                    non_malignant_percentage = 100.0 - prob_percentage
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Malignant-Suspicious probability", f"{prob_percentage:.1f}%")
                    with col2:
                        st.metric("Non-malignant probability", f"{non_malignant_percentage:.1f}%")
                        
                    st.progress(float(probability))
                    st.caption("*(Note: This probability is a statistical model output, not a measure of medical certainty.)*")
                    
                    st.markdown("---")
                    
                    # C. Decision threshold
                    st.markdown("### C. Decision threshold context")
                    st.info(
                        "**Decision threshold: 50.0%**\n\n"
                        "At the current threshold, probabilities at or above 50% produce the **Malignant-Suspicious** model output. "
                        "Probabilities below 50% produce the **Non-malignant** model output."
                    )
                    
                    st.markdown("---")
                    
                    # D. Model output strength (Threshold distance logic)
                    st.markdown("### D. Model output strength")
                    probability_margin = abs(probability - 0.5)
                    margin_percentage = probability_margin * 100
                    
                    if probability_margin < 0.10:
                        conf_interpretation = "Near-threshold model output"
                        st.info(f"**{conf_interpretation}**\n\n"
                                "The estimated model probability is close to the current decision threshold, so the classification is sensitive to small changes in model output.")
                        st.caption(f"**Distance from decision threshold:** {margin_percentage:.1f} percentage points")
                    elif probability_margin < 0.25:
                        conf_interpretation = "Moderate distance from threshold"
                        st.info(f"**{conf_interpretation}**\n\n"
                                "The model probability is neither very close to nor far from the current decision threshold.")
                        st.caption(f"**Distance from decision threshold:** {margin_percentage:.1f} percentage points")
                    else:
                        conf_interpretation = "Model output is farther from the decision threshold."
                        st.info(f"**{conf_interpretation}**\n\n"
                                "The model probability is farther from the current classification threshold.")
                        st.caption(f"**Distance from decision threshold:** {margin_percentage:.1f} percentage points")
                        
                    st.markdown("---")
                    
                    # E. Safety disclaimer
                    st.markdown("### E. Safety disclaimer")
                    st.warning(
                        "**Disclaimer:** This project is an AI research and educational prototype. "
                        "Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. "
                        "The system is not a medical diagnostic device and should not be used to make clinical decisions."
                    )
                
                st.markdown("---")
                
                # -----------------------------------------------------------------------------
                # GRAD-CAM EXPLAINABILITY
                # -----------------------------------------------------------------------------
                st.subheader("Grad-CAM Explainability")
                st.markdown("Grad-CAM is an explainability visualization that highlights image regions that contributed more strongly to the model output. It describes model behavior and is not a medical diagnostic map.")
                
                try:
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
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(vis_img, caption="Uploaded image", use_container_width=True)
                    with col2:
                        st.image(cam_image, caption="Grad-CAM overlay", use_container_width=True)
                    
                    st.caption("Highlighted regions indicate areas contributing more strongly to the model output.")
                    st.caption("Grad-CAM provides a visual explanation of the current model output; it does not establish the medical meaning of the highlighted region.")
                except Exception:
                    st.warning("Grad-CAM visualization could not be generated for this image.")
                
                # -----------------------------------------------------------------------------
                # SAVE PREDICTION HISTORY
                # -----------------------------------------------------------------------------
                save_prediction_history(
                    image_name=uploaded_file.name,
                    prediction=prediction_text,
                    malignant_probability=float(probability),
                    non_malignant_probability=float(1.0 - probability),
                    confidence=conf_interpretation,
                    image_quality=quality_data["overall_quality"]
                )

    except Exception as e:
        # Handle invalid/corrupted images gracefully
        st.error(f"Error processing the uploaded image. Please ensure it is a valid image file. Details: {e}")

# -----------------------------------------------------------------------------
# PREDICTION HISTORY UI
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("Prediction History")
st.caption("Previous model outputs recorded locally during this application's use. Prediction history is stored locally in history/prediction_history.csv.")

history_records = load_prediction_history()

if not history_records:
    st.info("No prediction history is available yet.")
else:
    # Newest record first
    history_records.reverse()
    
    formatted_history = []
    malignant_count = 0
    non_malignant_count = 0
    
    for record in history_records:
        try:
            mal_prob_str = record.get("malignant_probability")
            non_mal_prob_str = record.get("non_malignant_probability")
            
            if mal_prob_str is None or non_mal_prob_str is None:
                continue
                
            mal_prob = float(mal_prob_str) * 100
            non_mal_prob = float(non_mal_prob_str) * 100
            
            prediction_val = record.get("prediction", "")
            if "Malignant" in prediction_val and "Non" not in prediction_val:
                malignant_count += 1
            elif "Non-malignant" in prediction_val:
                non_malignant_count += 1
                
            formatted_history.append({
                "Timestamp": record.get("timestamp", ""),
                "Image": record.get("image_name", ""),
                "Model prediction": prediction_val,
                "Malignant probability": f"{mal_prob:.1f}%",
                "Non-malignant probability": f"{non_mal_prob:.1f}%",
                "Model output strength": record.get("confidence", ""),
                "Image quality": record.get("image_quality", "")
            })
        except (ValueError, TypeError):
            # Skip malformed row
            continue
            
    if not formatted_history:
        st.info("No valid prediction history available.")
    else:
        st.markdown(f"**Total recorded model outputs: {len(formatted_history)}** "
                    f"(Malignant-Suspicious: {malignant_count}, Non-malignant: {non_malignant_count})")
                    
        st.dataframe(
            formatted_history, 
            use_container_width=True,
            hide_index=True,
            column_config={
                "Timestamp": st.column_config.TextColumn(width="medium"),
                "Image": st.column_config.TextColumn(width="medium"),
                "Model prediction": st.column_config.TextColumn(width="medium"),
                "Malignant probability": st.column_config.TextColumn(width="small"),
                "Non-malignant probability": st.column_config.TextColumn(width="small"),
                "Model output strength": st.column_config.TextColumn(width="large"),
                "Image quality": st.column_config.TextColumn(width="medium"),
            }
        )
