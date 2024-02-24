import pytesseract
from PIL import Image

def ocr_image(image_path):
    # Open the image using PIL (Python Imaging Library)
    with Image.open(image_path) as img:
        # Perform OCR using pytesseract
        text = pytesseract.image_to_string(img)
    return text
