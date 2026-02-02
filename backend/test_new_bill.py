"""
Test OCR on the new bill image
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import extract_text_from_image, parse_bill_data
from datetime import date

# Path to the bill image
bill_image = r"C:\Users\Manasai stanly\.gemini\antigravity\brain\c5f2db11-5da7-4902-ae80-d864d464ccd0\uploaded_media_1770036660074.jpg"

print("="*80)
print("TESTING NEW BILL OCR")
print("="*80)

# Extract text
print("\n📄 EXTRACTING TEXT...\n")
text = extract_text_from_image(bill_image)
print("Raw Text:")
print(text)

# Parse data
print("\n🔍 PARSING DATA...\n")
parsed_data = parse_bill_data(text, uploaded_date=date.today())

print("\n✅ PARSED RESULTS:")
print(f"   Units: {parsed_data['units']}")
print(f"   Amount: ₹{parsed_data['amount']}")
print(f"   Date: {parsed_data['date']}")

# Save to file
with open("new_bill_test_results.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("NEW BILL OCR TEST\n")
    f.write("="*80 + "\n\n")
    f.write("Raw Text:\n")
    f.write(text + "\n\n")
    f.write("="*80 + "\n")
    f.write("PARSED RESULTS:\n")
    f.write(f"Units: {parsed_data['units']}\n")
    f.write(f"Amount: ₹{parsed_data['amount']}\n")
    f.write(f"Date: {parsed_data['date']}\n")

print("\n" + "="*80)
print("Results saved to new_bill_test_results.txt")
print("="*80)
