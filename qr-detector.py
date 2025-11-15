import zxingcpp
from PIL import Image
import cv2
import numpy as np
import sys

def decode_qr(image, description):
    """Helper function to try decoding and print results"""
    print(f"Attempting with: {description}")
    try:
        # read_barcodes accepts both PIL Images and NumPy arrays
        results = zxingcpp.read_barcodes(image)
        
        if results:
            print(f"\n--- SUCCESS (using {description}) ---")
            for res in results:
                print(f"  Text:     '{res.text}'")
                print(f"  Format:   {res.format}")
            return True
    except Exception as e:
        print(f"  Error while trying {description}: {e}")
    
    print("  ...failed.")
    return False

try:
    # --- Load images ---
    # Load with PIL (for the first attempt)
    pil_img = Image.open("IMG_9373.JPG")

    '''
    Image Object:
    When you load an image file (like a JPEG, PNG, or GIF) using Pillow's Image.open() function, it creates an Image object. This object represents the image data in memory and allows you to perform various operations on it, such as:

    Resizing and Cropping: Changing the dimensions or selecting a portion of the image.
    Filtering: Applying effects like blurring, sharpening, or edge detection.
    Color Manipulation: Adjusting brightness, contrast, or converting color modes.
    Saving: Storing the modified image back to a file.
    '''
    
    # Load with OpenCV (for all processing)
    # Note: imread loads as BGR, but we'll grayscale it immediately
    cv_img = cv2.imread("IMG_9373.JPG")
    
    # Convert to grayscale, as all decoders prefer this
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # --- Start decoding attempts ---

    # Attempt 1: Original PIL Image (what we did before)
    if decode_qr(pil_img, "Original PIL Image"):
        sys.exit()

    # Attempt 2: Grayscale OpenCV Image (NumPy array)
    if decode_qr(gray, "Grayscale OpenCV Image"):
        sys.exit()

    # Attempt 3: Histogram Equalization (boosts contrast)
    equalized = cv2.equalizeHist(gray)
    if decode_qr(equalized, "Equalized Contrast"):
        sys.exit()
        
    # Attempt 4: Sharpened Image
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    if decode_qr(sharpened, "Sharpened Image"):
        sys.exit()

    # Attempt 5: Adaptive Threshold (very powerful for uneven backgrounds)
    # This turns the image black/white based on local neighborhood brightness
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    if decode_qr(adaptive_thresh, "Adaptive Threshold"):
        sys.exit()

    # Attempt 6: Inverted Adaptive Threshold (some decoders prefer white on black)
    adaptive_thresh_inv = cv2.bitwise_not(adaptive_thresh)
    if decode_qr(adaptive_thresh_inv, "Inverted Adaptive Threshold"):
        sys.exit()

    print("\n--- All preprocessing attempts failed. ---")
    print("This is a very difficult QR code.")

except FileNotFoundError:
    print("Error: Please make sure the image is in the same directory.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
