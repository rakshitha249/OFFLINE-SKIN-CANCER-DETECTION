# Interview Questions and Answers

## A. Project Overview

**1. What was the main goal of this project?**
The goal was to build a complete, end-to-end offline machine learning pipeline for binary image classification—from data preprocessing and model fine-tuning to evaluation and local application deployment—as an AI research and educational prototype.

**2. What stack did you use?**
The core stack is Python, utilizing PyTorch and torchvision for deep learning, scikit-learn and pandas for data manipulation and splitting, and Streamlit for the local web application interface.

**3. Is this application intended for clinical use?**
Absolutely not. It is an AI research and educational prototype. The outputs are purely statistical estimated probabilities, and the system is not a medical diagnostic device.

**4. Why did you prioritize an offline-first architecture?**
To demonstrate how a complete, complex computer vision pipeline and explainability tools can be packaged and executed entirely on local hardware without relying on cloud computation or external APIs.

**5. What was the most challenging part of the pipeline?**
Managing the data leakage risk. Ensuring that images of the exact same physical lesion did not bleed across the training, validation, and test splits required careful implementation of `GroupShuffleSplit` using the metadata's `lesion_id`.

## B. Dataset

**1. Why did you use the HAM10000 dataset?**
It is a well-documented, publicly available, and highly cited benchmark dataset in dermatological machine learning, containing over 10,000 images with robust metadata including lesion-level identifiers.

**2. What are the seven original classes?**
Melanoma (MEL), Melanocytic nevi (NV), Basal cell carcinoma (BCC), Actinic keratoses and intraepithelial carcinoma / Bowen's disease (AKIEC), Benign keratosis-like lesions (BKL), Dermatofibroma (DF), and Vascular lesions (VASC).

**3. Why did you use binary grouping?**
To simplify a highly complex multi-class problem into a more straightforward binary classification task (Malignant-Suspicious vs. Non-malignant) suitable for evaluating foundational binary metrics like ROC-AUC and binary threshold dynamics.

**4. Why is lesion-level grouping critical in this dataset?**
Because multiple images were often taken of the same physical lesion. If you do a simple random split, images of the same lesion could end up in both the training and test sets, causing data leakage and artificially inflating test performance.

**5. How did you implement this split?**
I used scikit-learn's `GroupShuffleSplit`, grouping specifically on the `lesion_id` column, to create a 70/15/15 ratio for training, validation, and testing.

## C. Model

**1. Why did you choose EfficientNet-B0?**
EfficientNet-B0 offers an excellent balance between parameter efficiency and accuracy, making it ideal for a prototype intended to run inference locally on standard hardware (including CPUs).

**2. What is transfer learning, and how did you use it?**
Transfer learning involves taking a model pre-trained on a large dataset (like ImageNet) and adapting it to a specific task. I took the pre-trained backbone, replaced the final classification head with a single output neuron, and fine-tuned it on the HAM10000 images.

**3. Why use a single binary output neuron?**
Because it's a binary classification task. A single neuron outputting a raw logit allows us to apply a sigmoid function to retrieve a continuous probability between 0 and 1.

**4. Why did you use `BCEWithLogitsLoss`?**
It combines a Sigmoid layer and the Binary Cross Entropy Loss into one single class, which is numerically more stable than applying a sigmoid activation followed by a standard BCELoss.

**5. Why did you implement positive-class weighting?**
The dataset is heavily imbalanced toward the Non-malignant class (specifically the NV category). Applying a positive weight to the loss function penalizes the model more heavily for missing the minority positive class.

**6. What is fine-tuning in this context?**
After training just the new classification head, fine-tuning involves unfreezing some or all of the deeper convolutional layers in the backbone and training them at a much lower learning rate to adapt the feature extractors specifically to skin lesions.

**7. Why did you use a lower learning rate (0.00001) during fine-tuning?**
To prevent catastrophic forgetting. A large learning rate would aggressively overwrite the highly useful foundational features the model learned during its pre-training on ImageNet.

**8. How did you select the final checkpoint?**
By monitoring the ROC-AUC score on the validation set during training, ensuring we selected the model state with the best discriminative ability before overfitting occurred.

## D. Evaluation

**1. What was your final ROC-AUC?**
85.37% on the strictly held-out test set of 1,494 images.

**2. What does ROC-AUC measure?**
It measures the model's ability to distinguish between the positive and negative classes across all possible classification thresholds. It is threshold-independent.

**3. What was the Recall/Sensitivity at the 0.50 threshold?**
90.88%. The model correctly identified approximately 91% of the actual positive cases in the test set.

**4. Why was Precision much lower (39.53%)?**
Due to a high number of false positives (442). Because the dataset is imbalanced and the model was optimized to penalize false negatives, it aggressively flags borderline cases, leading to lower precision.

**5. What is the difference between the validation and test sets?**
The validation set is used during training to tune hyperparameters and select checkpoints. The test set is completely held out until the very end to provide an unbiased estimate of final model performance.

**6. Why shouldn't the test-set threshold analysis be considered "clinical optimization"?**
Because true clinical threshold optimization requires balancing specific clinical costs (e.g., the cost of a missed diagnosis vs. the cost of an unnecessary biopsy) using external, real-world data, not just shifting a mathematical boundary on a static test dataset.

**7. What did the error analysis reveal about false positives?**
It showed that over 97% of the false positives came from just two original classes: NV (nevi) and BKL.

**8. What did the error analysis reveal about false negatives?**
It showed that approximately 82.8% of false negatives were from the Melanoma (MEL) class.

**9. Are false positives clustered near the 0.50 threshold?**
Not entirely. While many are near the threshold, a significant portion are distributed higher up the probability range, indicating the model is strongly confident in some of its incorrect predictions.

**10. What does the Confusion Matrix tell us?**
At the 0.50 threshold, it provides the exact counts: True Negatives (734), False Positives (442), False Negatives (29), and True Positives (289).

## E. Explainability

**1. What is Grad-CAM?**
Gradient-weighted Class Activation Mapping. It's a technique used to produce visual explanations for decisions from CNN-based models.

**2. What does the Grad-CAM heatmap show in your app?**
It highlights the spatial regions of the image that had the strongest positive influence on the model's final logit output.

**3. What does it NOT prove?**
It does not prove that the highlighted region has any specific medical or anatomical significance. It only illustrates mathematical model behavior.

**4. Why did you include it?**
To provide transparency. In a black-box deep learning model, seeing what the model is "looking at" helps users trust that the model is focusing on the lesion rather than background artifacts (like a ruler or hair).

**5. How does Grad-CAM help understand model behavior?**
If the heatmap consistently highlights background skin or artifacts instead of the lesion itself, it indicates the model may have learned a spurious correlation rather than a generalized feature.

## F. Application

**1. Why did you use Streamlit?**
Streamlit allows for rapid development of data-focused, interactive web applications entirely in Python, without needing a separate frontend stack like React or a complex backend framework.

**2. How is inference performed?**
The Streamlit app loads the PyTorch checkpoint into memory (`@st.cache_resource`), applies the exact same preprocessing transformations used during validation, passes the tensor through the model, and applies a sigmoid function to the output logit.

**3. How does the offline operation work?**
Everything—the Python interpreter, the Streamlit server, the PyTorch engine, and the model weights—executes locally on the host machine CPU/GPU. No data is transmitted to an external inference endpoint.

**4. Where is the prediction history stored?**
It is appended to a local CSV file (`history/prediction_history.csv`) on the host machine.

**5. What happens if the Grad-CAM computation fails?**
The application handles the exception gracefully. It still displays the statistical model output and probabilities, while showing a localized warning that the visualization could not be generated.

## G. Limitations

**1. What are the limitations of the dataset?**
The HAM10000 dataset has a severe class imbalance (heavily skewed toward NV) and reflects the specific dermatoscopic imaging characteristics of its source institutions, which may not generalize to different lighting, cameras, or skin types.

**2. Why is binary simplification a limitation?**
Skin lesions exist on a highly nuanced spectrum. Forcing seven distinct conditions into two buckets removes critical diagnostic granularity.

**3. What is a key performance limitation of this model?**
The high false-positive rate. In a real-world scenario, this would result in a massive number of unnecessary alerts or referrals.

**4. Why is the 0.50 threshold a limitation?**
It is merely a default mathematical center point for a sigmoid output. It is arbitrary and has not been tuned for actual operational or clinical utility.

**5. What are the reproducibility limitations of the project?**
Because the raw dataset and the trained model weights are too large for Git, a fresh clone cannot run inference immediately. The user must supply the dataset and reproduce the training, which may yield minor variances due to hardware and random seed states.

**6. Is the model clinically validated?**
No. It has only been evaluated on a held-out test split from the same source distribution as the training data. There is no external or real-world clinical validation.

**7. How did you ensure the application doesn't present itself as a medical tool?**
I audited the UI language to remove words like "diagnosis," "safe," or "danger." The application uses terms like "statistical model output," "estimated probability," and prominently displays a safety disclaimer.

**8. If you were to continue this project, what would you improve?**
I would acquire external test datasets from different institutions to evaluate generalization, implement a multi-class architecture to avoid the binary simplification, and explore more advanced architectures or ensemble methods.
