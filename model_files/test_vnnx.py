import os
import numpy as np
from PIL import Image
import vbx.sim.vnnx as vnnx

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
MODEL_PATH = "model_cardboard.vnnx"
TEST_IMAGES_DIR = "/home/joeld/modelwork/Camera/test-dataset"

# Class Mapping (Alphabetical Order of training folders)
# 0: training-defective
# 1: training-undefective
CLASSES = ["DEFECTIVE", "NON-DEFECTIVE"]

# Normalization Constants (Same as your train.py)
MEAN = np.array([0.485, 0.456, 0.406])
STD = np.array([0.229, 0.224, 0.225])

def preprocess_image(image_path, input_shape):
    """
    Reads image, resizes to 224x224, and applies normalization.
    Returns: numpy array with shape (1, 224, 224, 3)
    """
    # 1. Open Image and convert to RGB
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error opening {image_path}: {e}")
        return None

    # 2. Resize to model input size (usually 224x224)
    # input_shape is usually [Batch, Height, Width, Channel]
    target_h, target_w = input_shape[1], input_shape[2] 
    img = img.resize((target_w, target_h))

    # 3. Convert to Float32 and Normalize
    img_data = np.array(img, dtype=np.float32)
    img_data = img_data / 255.0  # Scale 0-255 to 0-1
    img_data = (img_data - MEAN) / STD  # Normalize

    # 4. Add Batch Dimension
    img_data = np.expand_dims(img_data, axis=0)
    
    return img_data

def main():
    print(f"--- Loading Model: {MODEL_PATH} ---")
    if not os.path.exists(MODEL_PATH):
        print("Error: VNNX file not found!")
        return

    # Load the VNNX Model
    model = vnnx.Vnnx(MODEL_PATH)
    print(f"Model Input Shape: {model.input_shape}")

    # Get list of images
    if not os.path.exists(TEST_IMAGES_DIR):
        print(f"Error: Directory {TEST_IMAGES_DIR} not found.")
        return
        
    files = sorted([f for f in os.listdir(TEST_IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    print("\n" + "="*85)
    print(f"{'FILENAME':<20} | {'PREDICTED CLASS':<15} | {'CONFIDENCE':<10} | {'STATUS'}")
    print("="*85)

    for f in files:
        full_path = os.path.join(TEST_IMAGES_DIR, f)
        
        # Preprocess
        input_tensor = preprocess_image(full_path, model.input_shape)
        if input_tensor is None: continue

        # Run Inference
        results = model.run(input_tensor)
        
        # Get Probabilities (Flatten to 1D array)
        probs = results[0].flatten()
        
        # Get highest probability index
        pred_idx = np.argmax(probs)
        pred_label = CLASSES[pred_idx]
        confidence = probs[pred_idx]

        # Automatic Verification based on filename hints (d) or (nd)
        status = ""
        if "(d)" in f.lower():
            status = "✅ PASS" if pred_idx == 0 else "❌ FAIL"
        elif "(nd)" in f.lower():
            status = "✅ PASS" if pred_idx == 1 else "❌ FAIL"

        print(f"{f:<20} | {pred_label:<15} | {confidence:.4f}     | {status}")

    print("="*85)

if __name__ == "__main__":
    main()
