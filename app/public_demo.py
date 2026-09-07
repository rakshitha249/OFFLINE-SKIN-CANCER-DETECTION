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
import urllib.request


# Set the page configuration for a professional look
st.set_page_config(
    page_title="Skin Lesion Analyzer (Public Demo)",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"
)


# -----------------------------------------------------------------------------
# MODEL LOADING & DOWNLOADING (CACHED)
# -----------------------------------------------------------------------------
@st.cache_resource
def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    checkpoint_dir = "models"
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(checkpoint_dir, "best_finetuned_model.pth")
    
    if not os.path.exists(checkpoint_path):
        model_url = os.environ.get("MODEL_URL")
        if not model_url:
            return None, device, "MODEL_URL environment variable is not configured and local model is missing."
        try:
            urllib.request.urlretrieve(model_url, checkpoint_path)
        except Exception as e:
            return None, device, f"Failed to download model from MODEL_URL: {e}"

    model = models.efficientnet_b0(weights=None)
    num_ftrs = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=True),
        nn.Linear(num_ftrs, 1)
    )

    try:
        checkpoint = torch.load(
            checkpoint_path,
            map_location=device,
            weights_only=False
        )
        model.load_state_dict(checkpoint["model_state_dict"])
    except Exception as e:
        return None, device, f"Failed to load checkpoint: {e}"

    model.eval()
    model = model.to(device)

    return model, device, ""

model, device, error_msg = load_model()

if model is None:
    st.error(f"Application cannot start. {error_msg}")
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
# PREDICTION HISTORY (SESSION-ONLY)
# -----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state["history"] = []

def save_prediction_history(image_name, prediction, malignant_probability, non_malignant_probability, confidence, image_quality):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "timestamp": timestamp,
        "image_name": image_name,
        "prediction": prediction,
        "malignant_probability": malignant_probability,
        "non_malignant_probability": non_malignant_probability,
        "confidence": confidence,
        "image_quality": image_quality
    }
    st.session_state["history"].append(record)

def load_prediction_history():
    return list(st.session_state["history"])


# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
sidebar_css = """
<style>
/* Sidebar specific scoping */
[data-testid="stSidebar"] {
    min-width: 270px !important;
    max-width: 290px !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    width: 100% !important;
    border-radius: 10px !important;
    border: 1px solid rgba(128, 128, 128, 0.3) !important;
    background-color: transparent !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    border-color: #B87968 !important;
    color: #B87968 !important;
}
</style>
"""
st.sidebar.markdown(sidebar_css, unsafe_allow_html=True)

sidebar_html = f"""
<div style="text-align: center; margin-bottom: 30px; margin-top: 10px;">
    <div style="font-size: 32px; margin-bottom: 5px;">🔬</div>
    <div style="font-size: 20px; font-weight: 800; color: #B87968; letter-spacing: 1px; margin-bottom: 2px;">SKIN VISION</div>
    <div style="font-size: 13px; opacity: 0.7; font-weight: 600;">Public Demo Version</div>
</div>
<hr style="margin-bottom: 20px; border-color: rgba(128,128,128,0.15);">
<div style="font-size: 12px; font-weight: 700; letter-spacing: 1px; opacity: 0.5; margin-bottom: 20px;">NAVIGATION / INFORMATION</div>
<div style="margin-bottom: 18px;">
    <div style="font-size: 13px; opacity: 0.6; margin-bottom: 2px;">Model</div>
    <div style="font-size: 14.5px; font-weight: 600; opacity: 0.9;">EfficientNet-B0</div>
</div>
<div style="margin-bottom: 18px;">
    <div style="font-size: 13px; opacity: 0.6; margin-bottom: 2px;">Task</div>
    <div style="font-size: 14.5px; font-weight: 600; opacity: 0.9; line-height: 1.3;">Binary skin lesion<br>classification</div>
</div>
<div style="margin-bottom: 18px;">
    <div style="font-size: 13px; opacity: 0.6; margin-bottom: 2px;">Inference</div>
    <div style="font-size: 14.5px; font-weight: 600; opacity: 0.9;">Hosted</div>
</div>
<div style="margin-bottom: 18px;">
    <div style="font-size: 13px; opacity: 0.6; margin-bottom: 2px;">Dataset</div>
    <div style="font-size: 14.5px; font-weight: 600; opacity: 0.9;">HAM10000</div>
</div>
<div style="margin-bottom: 30px;">
    <div style="font-size: 13px; opacity: 0.6; margin-bottom: 2px;">Device</div>
    <div style="font-size: 14.5px; font-weight: 600; opacity: 0.9;">{device.type.upper()}</div>
</div>
<hr style="margin-bottom: 25px; border-color: rgba(128,128,128,0.15);">
"""
st.sidebar.markdown(sidebar_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN CONTENT AREA
# -----------------------------------------------------------------------------
main_header_html = """
<style>
/* Main Dashboard Primary Button Override */
[data-testid="stBaseButton-primary"] {
    background-color: #B87968 !important;
    border-color: #B87968 !important;
    color: #FFFFFF !important;
    transition: all 0.2s ease !important;
}
[data-testid="stBaseButton-primary"]:hover {
    background-color: #9C6353 !important;
    border-color: #9C6353 !important;
    color: #FFFFFF !important;
}
</style>
<div style="text-align: center; margin-bottom: 20px; margin-top: 10px;">
    <div style="font-size: 40px; margin-bottom: 5px;">🔬</div>
    <div style="font-size: 38px; font-weight: 800; color: #B87968; letter-spacing: 1.2px; margin-bottom: 5px;">SKIN VISION</div>
    <div style="font-size: 20px; font-weight: 600; margin-bottom: 10px; opacity: 0.9;">Public Demo — Hosted inference version</div>
    <div style="font-size: 15px; opacity: 0.7; line-height: 1.4; font-style: italic;">This hosted demonstration runs inference on the deployment server.<br>The original project also supports fully offline/local inference.</div>
</div>
<div style='display: flex; justify-content: center; gap: 10px; margin-bottom: 35px;'>
    <div style='padding: 5px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); opacity: 0.85;'>HOSTED INFERENCE</div>
    <div style='padding: 5px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); opacity: 0.85;'>LOCAL MODEL</div>
    <div style='padding: 5px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); opacity: 0.85;'>RESEARCH PROTOTYPE</div>
</div>
<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 20px; margin-bottom: 35px;">
    <div style="font-weight: 600; margin-bottom: 8px; opacity: 0.9; display: flex; align-items: center; gap: 8px;"><span style="font-size: 18px;">⚠️</span> Research & Educational Prototype</div>
    <div style="font-size: 14.5px; opacity: 0.8; line-height: 1.5;">This project is an AI research and educational prototype. Model probabilities represent statistical outputs from the trained model and are not measures of medical certainty. The system is not a medical diagnostic device and should not be used to make clinical decisions.</div>
</div>
"""
st.markdown(main_header_html, unsafe_allow_html=True)

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

# -----------------------------------------------------------------------------
# IMAGE UPLOADER & INFERENCE
# -----------------------------------------------------------------------------
upload_ui_css = """
<style>
/* Increase main content width for a better dashboard feel */
[data-testid="block-container"] {
    max-width: 900px !important;
}

/* Upload Section Card */
[data-testid="stFileUploader"] {
    background-color: var(--secondary-background-color) !important;
    border: 1px solid rgba(128, 128, 128, 0.15) !important;
    border-radius: 20px !important;
    padding: 32px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
    margin-top: 10px !important;
    margin-bottom: 25px !important;
}

/* Dropzone Styling */
[data-testid="stFileUploaderDropzone"] {
    background-color: var(--background-color) !important;
    border: 2px dashed rgba(184, 121, 104, 0.4) !important;
    border-radius: 12px !important;
    padding: 40px 20px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #B87968 !important;
    background-color: rgba(184, 121, 104, 0.04) !important;
}

/* Browse Button Styling */
[data-testid="stFileUploaderDropzone"] button {
    background-color: transparent !important;
    color: var(--text-color) !important;
    border: 1.5px solid rgba(184, 121, 104, 0.6) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 4px 18px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    border-color: #B87968 !important;
    color: #B87968 !important;
    background-color: rgba(184, 121, 104, 0.05) !important;
}
</style>
"""
st.markdown(upload_ui_css, unsafe_allow_html=True)

upload_header_html = """
<div style="margin-top: 40px; margin-bottom: 5px;">
    <div style="font-size: 24px; font-weight: 800; letter-spacing: 0.5px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #B87968;">01</span> ANALYZE A SKIN IMAGE
    </div>
</div>
<div style="font-size: 15px; opacity: 0.8; margin-bottom: 15px;">Upload a JPG, JPEG, or PNG image to generate a model output.</div>
<div style="display: flex; gap: 15px; font-size: 13.5px; opacity: 0.65; font-weight: 600; flex-wrap: wrap; margin-bottom: 25px;">
    <span>① Upload image</span>
    <span>→</span>
    <span>② Model analysis</span>
    <span>→</span>
    <span>③ Review output</span>
</div>
"""
st.markdown(upload_header_html, unsafe_allow_html=True)

# Create a file uploader that accepts JPG, JPEG, and PNG image formats
uploaded_file = st.file_uploader(
    "**Upload a skin image (JPG, JPEG, PNG)**",
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
                import base64
                from io import BytesIO

                # Encode the image to base64 for direct HTML injection
                buffered = BytesIO()
                image.convert("RGB").save(buffered, format="JPEG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()

                st.markdown("""
<div style="margin-top: 50px; margin-bottom: 25px;">
    <div style="font-size: 24px; font-weight: 800; letter-spacing: 0.5px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #B87968;">02</span> MODEL OUTPUT
    </div>
</div>
""", unsafe_allow_html=True)

                prob_percentage = probability * 100
                non_malignant_percentage = 100.0 - prob_percentage
                probability_margin = abs(probability - 0.5)
                margin_percentage = probability_margin * 100

                if probability_margin < 0.10:
                    conf_interpretation = "Near-threshold model output"
                    conf_explanation = "The estimated model probability is close to the current decision threshold, so the classification is sensitive to small changes in model output."
                elif probability_margin < 0.25:
                    conf_interpretation = "Moderate distance from threshold"
                    conf_explanation = "The model probability is neither very close to nor far from the current decision threshold."
                else:
                    conf_interpretation = "Farther from decision threshold"
                    conf_explanation = "The model probability is farther from the current classification threshold."

                # Left side: Image Card
                left_html = f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 18px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 13px; opacity: 0.6; margin-bottom: 16px; letter-spacing: 1px;">UPLOADED IMAGE</div>
    <img src="data:image/jpeg;base64,{img_b64}" style="width: 100%; border-radius: 12px; object-fit: cover;" />
    <div style="margin-top: 15px; font-size: 13px; opacity: 0.7; font-weight: 500;">{uploaded_file.name}</div>
</div>"""

                # Right side: Prediction Card
                right_html = f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 18px; padding: 32px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 13px; opacity: 0.6; margin-bottom: 12px; letter-spacing: 1px;">MODEL PREDICTION</div>
    <div style="font-size: 28px; font-weight: 800; color: var(--text-color); margin-bottom: 30px; letter-spacing: 0.5px;">{prediction_text}</div>
    <div style="margin-bottom: 8px; font-size: 14px; opacity: 0.8; font-weight: 600;">Estimated model probability</div>
    <div style="font-size: 42px; font-weight: 800; color: #B87968; margin-bottom: 35px; line-height: 1;">{prob_percentage:.1f}<span style="font-size: 24px;">%</span></div>
    <hr style="border-color: rgba(128,128,128,0.15); margin-bottom: 25px;">
    <div style="margin-bottom: 12px; font-size: 13px; opacity: 0.7; font-weight: 700;">PROBABILITY DISTRIBUTION</div>
    <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 4px; opacity: 0.9;">
        <span>Non-malignant</span>
        <span>{non_malignant_percentage:.1f}%</span>
    </div>
    <div style="width: 100%; background-color: rgba(128,128,128,0.15); border-radius: 8px; height: 8px; margin-bottom: 15px; overflow: hidden;">
        <div style="width: {non_malignant_percentage}%; background-color: #756968; height: 100%; border-radius: 8px;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 4px; opacity: 0.9;">
        <span>Malignant-Suspicious</span>
        <span>{prob_percentage:.1f}%</span>
    </div>
    <div style="width: 100%; background-color: rgba(128,128,128,0.15); border-radius: 8px; height: 8px; margin-bottom: 35px; overflow: hidden;">
        <div style="width: {prob_percentage}%; background-color: #B87968; height: 100%; border-radius: 8px;"></div>
    </div>
    <div style="background-color: var(--background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 20px;">
        <div style="font-weight: 700; font-size: 13px; opacity: 0.8; margin-bottom: 15px; display: flex; justify-content: space-between;">
            <span>Decision threshold</span>
            <span>50.0%</span>
        </div>
        <div style="position: relative; width: 100%; height: 2px; background-color: rgba(128,128,128,0.3); margin-bottom: 20px; margin-top: 10px;">
            <div style="position: absolute; left: 50%; top: -6px; width: 2px; height: 14px; background-color: var(--text-color); opacity: 0.5;"></div>
            <div style="position: absolute; left: {prob_percentage}%; top: -5px; width: 12px; height: 12px; border-radius: 50%; background-color: #B87968; transform: translateX(-50%); border: 2px solid var(--secondary-background-color);"></div>
        </div>
        <div style="font-size: 14px; font-weight: 600; margin-bottom: 6px;">{margin_percentage:.1f} percentage points from threshold</div>
        <div style="font-size: 13px; opacity: 0.7; margin-bottom: 15px;">{conf_interpretation}</div>
        <div style="font-size: 12.5px; opacity: 0.6; line-height: 1.4; font-style: italic;">{conf_explanation}</div>
    </div>
</div>"""

                col1, col2 = st.columns([1, 1.4], gap="medium")
                with col1:
                    st.markdown(left_html, unsafe_allow_html=True)
                with col2:
                    st.markdown(right_html, unsafe_allow_html=True)

                st.markdown("---")

                # -----------------------------------------------------------------------------
                # IMAGE QUALITY ASSESSMENT DISPLAY
                # -----------------------------------------------------------------------------
                quality_data = assess_image_quality(image)

                st.markdown("""<div style="margin-top: 50px; margin-bottom: 25px;">
    <div style="font-size: 24px; font-weight: 800; letter-spacing: 0.5px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #B87968;">03</span> IMAGE QUALITY
    </div>
</div>""", unsafe_allow_html=True)
                st.caption("Basic image characteristics are checked before reviewing the model output.")

                with st.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 12px; opacity: 0.6; margin-bottom: 12px; letter-spacing: 1px;">RESOLUTION</div>
    <div style="font-weight: 700; font-size: 16px; margin-bottom: 4px;">{quality_data['resolution_status']}</div>
    <div style="font-size: 14px; opacity: 0.7;">{quality_data['width']} × {quality_data['height']}</div>
</div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 12px; opacity: 0.6; margin-bottom: 12px; letter-spacing: 1px;">BRIGHTNESS</div>
    <div style="font-weight: 700; font-size: 16px; margin-bottom: 4px;">{quality_data['brightness_status']}</div>
    <div style="font-size: 14px; opacity: 0.7;">{quality_data['brightness']:.1f}</div>
</div>""", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 12px; opacity: 0.6; margin-bottom: 12px; letter-spacing: 1px;">SHARPNESS</div>
    <div style="font-weight: 700; font-size: 16px; margin-bottom: 4px;">{quality_data['sharpness_status']}</div>
    <div style="font-size: 14px; opacity: 0.7;">{quality_data['sharpness']:.1f}</div>
</div>""", unsafe_allow_html=True)

                    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

                    if quality_data["overall_quality"] != "Good":
                        warn_msg = "Prediction is still generated, but the image-quality assessment indicates that the uploaded image has characteristics outside the preferred range:\n"
                        for prob in quality_data["problems"]:
                            warn_msg += f"- {prob}\n"
                        st.warning(warn_msg)

                st.markdown("---")

                # -----------------------------------------------------------------------------
                # GRAD-CAM EXPLAINABILITY
                # -----------------------------------------------------------------------------
                st.markdown("""<div style="margin-top: 50px; margin-bottom: 25px;">
    <div style="font-size: 24px; font-weight: 800; letter-spacing: 0.5px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #B87968;">04</span> GRAD-CAM EXPLAINABILITY
    </div>
</div>""", unsafe_allow_html=True)
                st.caption("Grad-CAM provides a visualization of image regions that contributed more strongly to the model output.")
                st.caption("Grad-CAM is an explainability visualization that highlights image regions that contributed more strongly to the model output. It describes model behavior and is not a medical diagnostic map.")

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

                    # Convert to base64 for reliable layout rendering
                    from PIL import Image
                    buffered_vis = BytesIO()
                    vis_img.save(buffered_vis, format="JPEG")
                    vis_b64 = base64.b64encode(buffered_vis.getvalue()).decode()

                    buffered_cam = BytesIO()
                    Image.fromarray(cam_image).save(buffered_cam, format="JPEG")
                    cam_b64 = base64.b64encode(buffered_cam.getvalue()).decode()

                    col1, col2 = st.columns(2, gap="medium")
                    with col1:
                        st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 12px; opacity: 0.6; margin-bottom: 16px; letter-spacing: 1px;">ORIGINAL IMAGE</div>
    <img src="data:image/jpeg;base64,{vis_b64}" style="width: 100%; border-radius: 12px; object-fit: cover;" />
</div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 12px; opacity: 0.6; margin-bottom: 16px; letter-spacing: 1px;">GRAD-CAM OVERLAY</div>
    <img src="data:image/jpeg;base64,{cam_b64}" style="width: 100%; border-radius: 12px; object-fit: cover;" />
</div>""", unsafe_allow_html=True)

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
st.markdown("""<div style="margin-top: 50px; margin-bottom: 25px;">
    <div style="font-size: 24px; font-weight: 800; letter-spacing: 0.5px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #B87968;">05</span> PREDICTION HISTORY
    </div>
</div>""", unsafe_allow_html=True)
st.caption("Previous model outputs recorded during your current session.")
st.caption("Prediction history is stored temporarily and clears when you leave.")

history_records = load_prediction_history()

if not history_records:
    st.markdown("""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 30px; text-align: center; opacity: 0.8; margin-top: 20px;">
    No prediction history is available yet.
</div>""", unsafe_allow_html=True)
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

            # Recalculate output strength for display based on probability
            prob = float(mal_prob_str)
            probability_margin = abs(prob - 0.5)
            if probability_margin < 0.10:
                conf_interpretation = "Near-threshold model output"
            elif probability_margin < 0.25:
                conf_interpretation = "Moderate distance from threshold"
            else:
                conf_interpretation = "Farther from decision threshold"

            formatted_history.append({
                "Timestamp": record.get("timestamp", ""),
                "Image": record.get("image_name", ""),
                "Model prediction": prediction_val,
                "Malignant probability": f"{mal_prob:.1f}%",
                "Non-malignant probability": f"{non_mal_prob:.1f}%",
                "Model output strength": conf_interpretation,
                "Image quality": record.get("image_quality", "")
            })
        except (ValueError, TypeError):
            # Skip malformed row
            continue

    if not formatted_history:
        st.markdown("""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 30px; text-align: center; opacity: 0.8; margin-top: 20px;">
    No valid prediction history available.
</div>""", unsafe_allow_html=True)
    else:
        total_outputs = len(formatted_history)

        # Summary Cards
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 11px; opacity: 0.6; margin-bottom: 12px; letter-spacing: 1px;">TOTAL OUTPUTS</div>
    <div style="font-weight: 800; font-size: 28px; color: var(--text-color); line-height: 1;">{total_outputs}</div>
</div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 11px; opacity: 0.6; margin-bottom: 12px; letter-spacing: 1px;">MALIGNANT-SUSPICIOUS</div>
    <div style="font-weight: 800; font-size: 28px; color: var(--text-color); line-height: 1;">{malignant_count}</div>
</div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div style="background-color: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box;">
    <div style="font-weight: 700; font-size: 11px; opacity: 0.6; margin-bottom: 12px; letter-spacing: 1px;">NON-MALIGNANT</div>
    <div style="font-weight: 800; font-size: 28px; color: var(--text-color); line-height: 1;">{non_malignant_count}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

        st.markdown(f"**Total recorded model outputs: {total_outputs}**")

        table_html = "<div style='overflow-x: auto; width: 100%; box-sizing: border-box; border: 1px solid rgba(128,128,128,0.15); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.03);'><table style='width: 100%; table-layout: fixed; border-collapse: collapse; background-color: var(--secondary-background-color); margin: 0;'>"
        table_html += "<thead style='background-color: rgba(128,128,128,0.05); border-bottom: 1px solid rgba(128,128,128,0.15);'><tr style='font-size: 11px; font-weight: 700; letter-spacing: 1px; opacity: 0.6; text-transform: uppercase;'>"
        table_html += "<th style='padding: 8px 10px; text-align: left; width: 15%;'>Timestamp</th>"
        table_html += "<th style='padding: 8px 10px; text-align: left; width: 14%;'>Image</th>"
        table_html += "<th style='padding: 8px 10px; text-align: left; width: 16%;'>Model Prediction</th>"
        table_html += "<th style='padding: 8px 10px; text-align: left; width: 9%;'>Mal. Prob</th>"
        table_html += "<th style='padding: 8px 10px; text-align: left; width: 11%;'>Non-Mal. Prob</th>"
        table_html += "<th style='padding: 8px 10px; text-align: left; width: 24%;'>Output Strength</th>"
        table_html += "<th style='padding: 8px 10px; text-align: left; width: 11%;'>Quality</th>"
        table_html += "</tr></thead>"

        table_html += "<tbody style='font-size: 13.5px; opacity: 0.9;'>"
        for row in formatted_history:
            table_html += "<tr style='border-bottom: 1px solid rgba(128,128,128,0.1);'>"
            table_html += f"<td style='padding: 8px 10px; text-align: left;'>{row['Timestamp']}</td>"
            table_html += f"<td style='padding: 8px 10px; text-align: left; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;' title='{row['Image']}'>{row['Image']}</td>"
            table_html += f"<td style='padding: 8px 10px; text-align: left; font-weight: 600;'>{row['Model prediction']}</td>"
            table_html += f"<td style='padding: 8px 10px; text-align: left;'>{row['Malignant probability']}</td>"
            table_html += f"<td style='padding: 8px 10px; text-align: left;'>{row['Non-malignant probability']}</td>"
            table_html += f"<td style='padding: 8px 10px; text-align: left;'>{row['Model output strength']}</td>"
            table_html += f"<td style='padding: 8px 10px; text-align: left; white-space: nowrap;'>{row['Image quality']}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table></div>"

        st.markdown(table_html, unsafe_allow_html=True)
