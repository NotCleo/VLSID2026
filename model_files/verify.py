import numpy as np
import onnx
import tensorflow.lite as tflite
import os

# --- CONFIG ---
TFLITE_MODEL = "model_cardboard_quant.tflite"
ONNX_MODEL = "/home/joeld/modelwork/model_cardboard.onnx"  # Adjust if path differs

def check_tflite(path):
    print(f"\n--- Checking TFLite: {os.path.basename(path)} ---")
    try:
        interpreter = tflite.Interpreter(model_path=path)
        interpreter.allocate_tensors()
        
        # Check Input/Output details
        input_details = interpreter.get_input_details()[0]
        output_details = interpreter.get_output_details()[0]
        
        # Check a random tensor inside the model (tensor index 5 usually exists)
        # We iterate to find a weight tensor to be sure
        is_quantized = False
        tensor_details = interpreter.get_tensor_details()
        
        print(f"Input Dtype:  {input_details['dtype']}")
        print(f"Output Dtype: {output_details['dtype']}")
        
        # Count int8 vs float32 tensors
        int8_count = sum(1 for t in tensor_details if t['dtype'] == np.int8)
        float_count = sum(1 for t in tensor_details if t['dtype'] == np.float32)
        
        print(f"Total Tensors: {len(tensor_details)}")
        print(f"INT8 Tensors:  {int8_count}")
        print(f"FP32 Tensors:  {float_count}")

        # VectorBlox requires Input to be INT8 (specifically usually signed int8 or uint8)
        if input_details['dtype'] == np.int8 or input_details['dtype'] == np.uint8:
            print("✅ Input is Quantized (INT8/UINT8)")
        else:
            print("❌ Input is FLOAT32 (Not fully quantized for input)")

        # Heuristic for model weights
        if int8_count > float_count:
             print("✅ Model weights appear to be INT8 quantized.")
        else:
             print("⚠️ Model appears to be largely FLOAT32.")

    except Exception as e:
        print(f"Error checking TFLite: {e}")

def check_onnx(path):
    print(f"\n--- Checking ONNX: {os.path.basename(path)} ---")
    try:
        model = onnx.load(path)
        
        # Check Input Type
        # TensorProto.FLOAT = 1, UINT8 = 2, INT8 = 3
        input_tensor = model.graph.input[0]
        elem_type = input_tensor.type.tensor_type.elem_type
        
        type_map = {1: "FLOAT32", 2: "UINT8", 3: "INT8", 10: "FLOAT16"}
        type_str = type_map.get(elem_type, f"Unknown ({elem_type})")
        
        print(f"Input Name: {input_tensor.name}")
        print(f"Input Type: {type_str}")

        # Check a weight initializer (raw model weights)
        if len(model.graph.initializer) > 0:
            first_weight = model.graph.initializer[0]
            w_type = first_weight.data_type
            w_type_str = type_map.get(w_type, f"Unknown ({w_type})")
            print(f"First Weight Type: {w_type_str}")
            
            if w_type == 1:
                print("✅ Model is standard FP32.")
            else:
                print(f"⚠️ Model is {w_type_str}, not FP32.")
        
    except Exception as e:
        print(f"Error checking ONNX: {e}")

if __name__ == "__main__":
    check_tflite(TFLITE_MODEL)
    if os.path.exists(ONNX_MODEL):
        check_onnx(ONNX_MODEL)
    else:
        print(f"\nCould not find ONNX file at {ONNX_MODEL} to verify.")
