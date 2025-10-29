import cv2
import numpy as np
from google.colab import files
from IPython.display import Image, display
import matplotlib.pyplot as plt
import os

def robust_auto_crop(image_path, output_path=None, show_steps=False):
    img = cv2.imread(image_path)
    if img is None:
        print("Error loading image!")
        return

    original = img.copy()
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    threshed = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    threshed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel, iterations=2)
    threshed = cv2.morphologyEx(threshed, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        _, threshed = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    main_contour = contours[0]

    if cv2.contourArea(main_contour) < 500:
        return

    x, y, w_box, h_box = cv2.boundingRect(main_contour)

    pad = 3
    x = max(x - pad, 0)
    y = max(y - pad, 0)
    w_box = min(w_box + 2*pad, w - x)
    h_box = min(h_box + 2*pad, h - y)

    cropped = original[y:y+h_box, x:x+w_box]

    if output_path is None:
        base, ext = os.path.splitext(image_path)
        output_path = f"{base}_TIGHT_CROPPED{ext}"
    cv2.imwrite(output_path, cropped)

    if show_steps:
        plt.figure(figsize=(15, 8))

        plt.subplot(2, 3, 1)
        plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        plt.title("Original")
        plt.axis('off')

        plt.subplot(2, 3, 2)
        plt.imshow(gray, cmap='gray')
        plt.title("Grayscale")
        plt.axis('off')

        plt.subplot(2, 3, 3)
        plt.imshow(threshed, cmap='gray')
        plt.title("Thresholded")
        plt.axis('off')

        plt.subplot(2, 3, 4)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [main_contour], -1, 255, 2)
        plt.imshow(mask, cmap='gray')
        plt.title("Main Contour")
        plt.axis('off')

        plt.subplot(2, 3, 5)
        debug = original.copy()
        cv2.rectangle(debug, (x, y), (x+w_box, y+h_box), (0, 255, 0), 2)
        plt.imshow(cv2.cvtColor(debug, cv2.COLOR_BGR2RGB))
        plt.title("Bounding Box")
        plt.axis('off')

        plt.subplot(2, 3, 6)
        plt.imshow(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        plt.title("FINAL CROPPED")
        plt.axis('off')

        plt.tight_layout()
        plt.show()

    return output_path

uploaded = files.upload()

if uploaded:
    img_name = list(uploaded.keys())[0]

    cropped_path = robust_auto_crop(img_name, show_steps=True)

    if cropped_path and os.path.exists(cropped_path):
        files.download(cropped_path)
