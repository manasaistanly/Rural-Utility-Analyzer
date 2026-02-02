"""
Test OCR on the clear water bill
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import extract_text_from_image, parse_bill_data
from datetime import date

# Path to the bill image
bill_image = r"C:\Users\Manasai stanly\.gemini\antigravity\brain\c5f2db11-5da7-4902-ae80-d864d464ccd0\uploaded_media_1770042069711.png"

print("="*80)
print("TESTING CLEAR WATER BILL")
print("="*80)

# Extract text
print("\n📄 EXTRACTING TEXT...\n")
text = extract_text_from_image(bill_image)
print("Raw Text (first 1000 chars):")
print(text[:1000])
print("\n" + "="*80)

# Parse data
print("\n🔍 PARSING DATA...\n")
parsed_data = parse_bill_data(text, uploaded_date=date.today())

print("\n✅ PARSED RESULTS:")
print(f"   Units: {parsed_data['units']}")
print(f"   Amount: ₹{parsed_data['amount']}")
print(f"   Date: {parsed_data['date']}")

# Expected values
print("\n📊 EXPECTED VALUES:")
print("   Units: 32 CBM")
print("   Amount: ₹890.18 (Current Bill) or ₹1066.18 (Total)")
print("   Date: June 2024")

# Save to file
with open("clear_water_bill_results.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("CLEAR WATER BILL TEST\n")
    f.write("="*80 + "\n\n")
    f.write("Raw Text:\n")
    f.write(text + "\n\n")
    f.write("="*80 + "\n")
    f.write("PARSED RESULTS:\n")
    f.write(f"Units: {parsed_data['units']}\n")
    f.write(f"Amount: ₹{parsed_data['amount']}\n")
    f.write(f"Date: {parsed_data['date']}\n")
    f.write("\nEXPECTED:\n")
    f.write("Units: 32 CBM\n")
    f.write("Amount: ₹890.18 or ₹1066.18\n")

print("\n" + "="*80)
print("Results saved to clear_water_bill_results.txt")
print("="*80)
