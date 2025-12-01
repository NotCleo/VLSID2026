#!/bin/bash
set -e

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
# Paths to your files
ONNX_PATH="/home/joeld/modelwork/model_cardboard.onnx"
CALIB_PATH="/home/joeld/modelwork/calibdata/calibration_224x224x3.npy"
OUTPUT_TFLITE="model_cardboard_quant.tflite"
PRE_TFLITE="model_cardboard.pre.tflite"

# ImageNet Constants (used in your train.py)
# Mean: 0.485, 0.456, 0.406
# Std:  0.229, 0.224, 0.225

# ------------------------------------------------------------------
# 1. ACTIVATE ENVIRONMENT
# ------------------------------------------------------------------
echo "Checking and activating VBX Python Environment..."
if [ -z $VBX_SDK ]; then
    echo "\$VBX_SDK not set. Please run 'source setup_vars.sh' from the SDK's root folder" && exit 1
fi
source $VBX_SDK/vbx_env/bin/activate

# ------------------------------------------------------------------
# 2. RUN ONNX2TF
# ------------------------------------------------------------------
# We use the same Mean/Std as your train.py.
# Note: We use "-cind input" because your train.py used input_names=["input"]
echo "Running ONNX2TF to generate INT8 Quantized TFLite..."

if [ ! -f $OUTPUT_TFLITE ]; then
   onnx2tf \
   -cind input "$CALIB_PATH" \
   [[[[0.485,0.456,0.406]]]] [[[[0.229,0.224,0.225]]]] \
   -i "$ONNX_PATH" \
   --output_signaturedefs \
   --output_integer_quantized_tflite
   
   # onnx2tf saves the output in a folder named 'saved_model' usually
   # We allow for the specific naming convention onnx2tf uses
   if [ -f saved_model/model_cardboard_full_integer_quant.tflite ]; then
       cp saved_model/model_cardboard_full_integer_quant.tflite $OUTPUT_TFLITE
       echo "Quantization successful. Copied to $OUTPUT_TFLITE"
   else
       echo "Error: Expected output file not found in saved_model directory."
       exit 1
   fi
fi

# ------------------------------------------------------------------
# 3. TFLITE PREPROCESS (VectorBlox Specific)
# ------------------------------------------------------------------
# This step adjusts the TFLite input tensors for the hardware accelerator.
# It converts the 0-1 Float Mean/Std into 0-255 Integer domain values.
# Calculation: Value * 255
# Mean: 0.485*255=123.675, 0.456*255=116.28, 0.406*255=103.53
# Scale: 0.229*255=58.395, 0.224*255=57.12, 0.225*255=57.375

echo "Running TFLite Preprocess..."
if [ -f $OUTPUT_TFLITE ]; then
   tflite_preprocess $OUTPUT_TFLITE \
   --mean 123.675 116.28 103.53 \
   --scale 58.395 57.12 57.375
fi

# ------------------------------------------------------------------
# 4. COMPILE TO VNNX (Optional - for next step)
# ------------------------------------------------------------------
# If you want to go all the way to VNNX now, uncomment the lines below.
# Ensure you choose the correct config (V1000 is common for PolarFire SoC).

# if [ -f $PRE_TFLITE ]; then
#     echo "Generating VNNX for V1000 configuration..."
#     vnnx_compile -c V1000 -t $PRE_TFLITE -o model_cardboard.vnnx
#     echo "VNNX generation complete: model_cardboard.vnnx"
# fi

echo "Done."
deactivate
