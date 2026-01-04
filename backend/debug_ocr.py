import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import extract_text_from_image, parse_bill_data

image_path = r"C:/Users/Manasai stanly/.gemini/antigravity/brain/a9e4978f-ba16-4989-ab2d-1b0592f2706b/uploaded_image_1767535509448.jpg"

print(f"Testing OCR on: {image_path}")

if not os.path.exists(image_path):
    print("Error: Image file not found at path.")
    sys.exit(1)

raw_text = extract_text_from_image(image_path)
print("-" * 20)
print("RAW EXTRACTED TEXT:")
print("-" * 20)
print(raw_text)
print("-" * 20)

parsed = parse_bill_data(raw_text)
print("PARSED DATA:")
print(parsed)
