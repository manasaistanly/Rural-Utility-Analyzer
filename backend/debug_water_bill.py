"""
Debug water bill OCR with verbose output to terminal
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import extract_text_from_image, parse_bill_data
from datetime import date

# Path to the bill image
bill_image = r"C:\Users\Manasai stanly\.gemini\antigravity\brain\c5f2db11-5da7-4902-ae80-d864d464ccd0\uploaded_media_1770041466920.jpg"

print("="*80)
print("TESTING WATER BILL OCR - VERBOSE MODE")
print("="*80)

# Extract text
print("\n📄 EXTRACTING TEXT...\n")
text = extract_text_from_image(bill_image)

# Show key sections of the OCR text
lines = text.split('\n')
print("\nKey OCR Lines (first 50):")
for i, line in enumerate(lines[:50], 1):
    if line.strip():
        print(f"{i}: {line}")

# Parse data
print("\n" + "="*80)
print("\n🔍 PARSING DATA (watch for OCR: messages)...\n")
parsed_data = parse_bill_data(text, uploaded_date=date.today())

print("\n" + "="*80)
print("\n✅ FINAL PARSED RESULTS:")
print(f"   Units: {parsed_data['units']}")
print(f"   Amount: ₹{parsed_data['amount']}")
print(f"   Date: {parsed_data['date']}")
print("="*80)
