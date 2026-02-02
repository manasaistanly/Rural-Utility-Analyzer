import sys
import os
from datetime import date

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import extract_text_from_image, parse_bill_data

# Test images provided by user
test_images = [
    r"C:/Users/Manasai stanly/.gemini/antigravity/brain/c5f2db11-5da7-4902-ae80-d864d464ccd0/uploaded_media_0_1769852017431.jpg",
    r"C:/Users/Manasai stanly/.gemini/antigravity/brain/c5f2db11-5da7-4902-ae80-d864d464ccd0/uploaded_media_1_1769852017431.jpg"
]

# Open output file
with open("ocr_test_results.txt", "w", encoding="utf-8") as output_file:
    def log(msg):
        print(msg)
        output_file.write(msg + "\n")
    
    log("=" * 80)
    log("TESTING IMPROVED OCR DATE EXTRACTION")
    log("=" * 80)
    
    for idx, image_path in enumerate(test_images, 1):
        log(f"\n{'='*80}")
        log(f"TEST {idx}: {os.path.basename(image_path)}")
        log("=" * 80)
        
        if not os.path.exists(image_path):
            log(f"❌ Image not found: {image_path}")
            continue
        
        try:
            # Extract text
            log("\n📄 EXTRACTING TEXT...")
            raw_text = extract_text_from_image(image_path)
            log(f"\nRaw Text:\n{raw_text}\n")
            
            # Parse with uploaded date fallback
            log("🔍 PARSING DATA (with uploaded date fallback)...")
            uploaded_date = date.today()
            parsed_data = parse_bill_data(raw_text, uploaded_date=uploaded_date)
            
            log("\n✅ PARSED RESULTS:")
            log(f"   Units: {parsed_data['units']}")
            log(f"   Amount: ₹{parsed_data['amount']}")
            log(f"   Date: {parsed_data['date']}")
            
            if parsed_data['date']:
                from datetime import datetime
                try:
                    bill_date = datetime.strptime(parsed_data['date'], "%Y-%m-%d")
                    if bill_date.year < 2000 or bill_date.year > 2050:
                        log(f"   ⚠️  WARNING: Date year {bill_date.year} is outside valid range!")
                    else:
                        log(f"   ✅ Date is valid (year: {bill_date.year})")
                except Exception as e:
                    log(f"   ❌ Date parsing error: {e}")
            
        except Exception as e:
            log(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    log("\n" + "=" * 80)
    log("TEST COMPLETE - Results saved to ocr_test_results.txt")
    log("=" * 80)

print("\nResults written to ocr_test_results.txt")
