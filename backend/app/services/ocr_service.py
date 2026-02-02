from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re
import os
import subprocess
import tempfile

# Explicitly configuration for Tesseract on Windows
# This ensures it works even if not in System PATH
base_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\Manasai stanly\AppData\Local\Tesseract-OCR\tesseract.exe',
    r'C:\Users\Manasai stanly\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
]

for path in base_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        print(f"DEBUG: Set Tesseract path to {path}")
        break

def preprocess_image(image_path: str) -> Image.Image:
    """
    Enhance image for better OCR accuracy.
    1. Grayscale
    2. Increase Contrast
    3. Sharpen
    """
    try:
        img = Image.open(image_path)
        
        # Convert to Grayscale
        img = img.convert('L')
        
        # Limit max dimension before upscaling to avoid massive images
        if max(img.width, img.height) > 4000:
             # Don't upscale if already huge
             pass
        else:
            # Upscale (2x) is usually enough, 4x is overkill and causes timeouts
            img = img.resize((img.width * 2, img.height * 2), Image.Resampling.BICUBIC)
        
        # Increase Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Binarize (Thresholding)
        # 140 was the "sweet spot" that found the text at all
        img = img.point(lambda x: 0 if x < 140 else 255, '1')
        
        return img
        
        return img
    except Exception as e:
        print(f"Preprocessing Error: {e}")
        return Image.open(image_path) # Fallback to original

def extract_text_from_image(image_path: str) -> str:
    try:
        if not os.path.exists(image_path):
            return ""
        
        # 1. Preprocess
        processed_img = preprocess_image(image_path)
        
        # Save processed image to temp file for Tesseract to read
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            processed_img.save(tmp.name)
            tmp_path = tmp.name
            
        try:
            # 2. Find Tesseract executable
            tesseract_cmd = "tesseract"
            for path in base_paths:
                if os.path.exists(path):
                    tesseract_cmd = path
                    break
            
            # 3. Run Tesseract with multiple PSM modes for better coverage
            # PSM 6: Assume uniform block of text
            # PSM 11: Sparse text, find as much text as possible
            
            all_text = []
            
            # First pass: PSM 6 (standard)
            result1 = subprocess.run(
                [tesseract_cmd, tmp_path, "stdout", "--oem", "3", "--psm", "6"],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            if result1.returncode == 0:
                all_text.append(result1.stdout.strip())
            
            # Second pass: PSM 11 (sparse text) - catches missed sections
            result2 = subprocess.run(
                [tesseract_cmd, tmp_path, "stdout", "--oem", "3", "--psm", "11"],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            if result2.returncode == 0:
                all_text.append(result2.stdout.strip())
            
            # Combine both results (longer one usually has more info)
            combined = "\n".join(all_text)
            return combined if combined.strip() else all_text[0] if all_text else ""
            
        except subprocess.TimeoutExpired:
            print("ERROR: OCR Timed out (10s limit exceeded)")
            return ""
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def validate_and_normalize_date(date_str: str, uploaded_date=None):
   
    from datetime import datetime, date as dt_date
    
    if not date_str:
        return None
    
    # Clean the date string
    date_str = date_str.strip()
    
    # Define date format patterns (DD/MM/YYYY variants first as they're most common in Indian bills)
    formats_to_try = [
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",  # DD/MM/YYYY variants
        "%d/%m/%y", "%d-%m-%y", "%d.%m.%y",  # DD/MM/YY variants  
        "%Y-%m-%d", "%Y/%m/%d",               # YYYY-MM-DD variants (for database format)
    ]
    
    current_year = dt_date.today().year
    current_month = dt_date.today().month
    
    for fmt in formats_to_try:
        try:
            parsed = datetime.strptime(date_str, fmt)
            day = parsed.day
            month = parsed.month
            year = parsed.year
            
            # Validate day and month ranges
            if not (1 <= day <= 31) or not (1 <= month <= 12):
                continue
            
            # Handle 2-digit years
            if year < 100:
                if year <= 50:
                    year += 2000
                else:
                    year += 1900
                parsed = parsed.replace(year=year)
                year = parsed.year
            
            # Production-level year validation and correction
            if year < 2000 or year > 2050:
                year_str = str(year)
                fixed_year = None
                
                # Strategy 1: Check for digit transposition patterns
                if len(year_str) == 4:
                    digits = list(year_str)
                    digit_set = set(digits)
                    
                    # Most common: Check for recent years (2020-2026)
                    for target_year in range(current_year, current_year - 6, -1):
                        target_digits = set(str(target_year))
                        # If at least 3 out of 4 digits match, likely the target year
                        if len(digit_set & target_digits) >= 3:
                            fixed_year = target_year
                            print(f"OCR: Corrected {year} -> {fixed_year} (digit match)")
                            break
                    
                    # Fallback: Check specific patterns
                    if not fixed_year:
                        # Pattern: 1673 → 24 is in there, month is 01, so likely 2024-01-24
                        if '2' in digit_set and '4' in digit_set:
                            fixed_year = 2024
                            print(f"OCR: Corrected {year} -> {fixed_year} (contains 2,4)")
                        elif '2' in digit_set and '3' in digit_set:
                            fixed_year = 2023
                            print(f"OCR: Corrected {year} -> {fixed_year} (contains 2,3)")
                        elif '2' in digit_set and '5' in digit_set:
                            fixed_year = 2025
                            print(f"OCR: Corrected {year} -> {fixed_year} (contains 2,5)")
                        elif '2' in digit_set and '6' in digit_set:
                            fixed_year = 2026
                            print(f"OCR: Corrected {year} -> {fixed_year} (contains 2,6)")
                
                # Strategy 2: If year parsing failed as YYYY-MM-DD, might be DD-MM-YYYY with scrambled year
                # Example: "24-01-1673" should be "24-01-2024"
                if not fixed_year and fmt.startswith("%Y"):
                    # This was parsed as YYYY-MM-DD but year is invalid
                    # The "year" might actually be the day, swap and retry
                    if day <= 12 and year <= 31:  # Possible day/year swap
                        print(f"OCR: Detected possible day/year swap in {date_str}")
                        continue  # Try next format
                
                if fixed_year:
                    try:
                        parsed = parsed.replace(year=fixed_year)
                        year = fixed_year
                    except ValueError:
                        # Date doesn't exist (e.g., Feb 30)
                        print(f"OCR: Invalid date after year correction: {day}/{month}/{fixed_year}")
                        continue
                else:
                    # Can't fix this date
                    print(f"OCR: Cannot fix invalid year {year} in {date_str}")
                    continue
            
            # Final validation checks
            year = parsed.year
            
            # Year must be in valid range
            if year < 2000 or year > 2050:
                continue
            
            # Date should not be in the future (bills can't be from future)
            if parsed.date() > dt_date.today():
                # Allow up to 1 day in future for timezone differences
                if (parsed.date() - dt_date.today()).days > 1:
                    print(f"OCR: Rejecting future date: {parsed.date()}")
                    continue
            
            # Date should not be too old for utility bills (usually within last 5 years)
            years_old = (dt_date.today() - parsed.date()).days / 365.25
            if years_old > 10:
                print(f"OCR: Date too old ({years_old:.1f} years): {parsed.date()}")
                continue
            
            # Validate the date actually exists (handles Feb 30, etc.)
            try:
                validated_date = dt_date(year, month, day)
            except ValueError:
                print(f"OCR: Invalid date: {day}/{month}/{year}")
                continue
            
            # Success - return normalized date
            return validated_date.strftime("%Y-%m-%d")
            
        except ValueError as e:
            # Failed to parse with this format, try next
            continue
    
    # No valid date found
    return None


def parse_bill_data(text: str, uploaded_date=None):
    """
    Robust Regex Parser for Indian Electricity/Water Bills.
    
    Args:
        text: OCR extracted text from bill
        uploaded_date: Fallback date to use if no valid date found in bill
    """
    from datetime import datetime, date
    
    data = {
        "units": 0.0,
        "amount": 0.0,
        "date": None
    }
    
    # --- 1. PRODUCTION-GRADE UNITS PARSING ---
    # Context-aware extraction with OCR error handling
    
    # PRIORITY 1: Try to calculate from meter readings (most reliable for water bills)
    calculated_units = None
    print("OCR: Attempting to calculate units from meter readings...")
    
    # Enhanced patterns for Indian water bills (Present/Prev readings)
    pres_patterns = [
        r'(?i)(?:Present|Pres|Current)(?:\s*Rdg)?(?:.|\n){0,50}?[:=-]?\s*(\d{5,})',
        r'(?i)(?:ಇಂದಿನ|ಆಂSೇ.*?ಸ್ವಚನ)(?:.|\n){0,50}?(\d{5,})',  # Kannada for Present
    ]
    prev_patterns = [
        r'(?i)(?:Previous|Prev|Earlier)(?:\s*Rdg)?(?:.|\n){0,50}?[:=-]?\s*(\d{5,})',
        r'(?i)(?:ಹಿಂದಿನ|ಮೊದಲ.*?ಸ್ವಚನ)(?:.|\n){0,50}?(\d{5,})',  # Kannada for Previous
    ]
    
    present_reading = None
    prev_reading = None
    
    # Try to find Present reading
    for pattern in pres_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                present_reading = int(match.group(1))
                print(f"OCR: Found Present reading: {present_reading}")
                break
            except (ValueError, IndexError):
                continue
    
    # Try to find Previous reading
    for pattern in prev_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                prev_reading = int(match.group(1))
                print(f"OCR: Found Previous reading: {prev_reading}")
                break
            except (ValueError, IndexError):
                continue
    
    # Calculate if both found
    if present_reading and prev_reading and present_reading > prev_reading:
        calculated_units = present_reading - prev_reading
        print(f"OCR: Calculated units: {present_reading} - {prev_reading} = {calculated_units}")
    
    # PRIORITY 2: Extract from direct consumption fields
    units_patterns = [
        # HIGHEST PRIORITY - Water bill specific consumption labels
        (r'(?i)Consumption[:\s]+(\d+\.?\d*)\s*(?:Cubic\s*Meter|CBM)', 12),
        (r'(?i)Consumption[:\s]+(\d+\.?\d*)\s*(?:L[it]?t?r?e?s?|KL)', 12),
        
        # High priority - explicit unit labels
        (r'(?i)(?:Units\s*Consumed|Consumed\s*Units)(?:.|\n){0,20}?[:=-]?\s*(\d+\.?\d*)', 10),
        (r'(?i)(?:Units\s*Billed|Billed\s*Units)(?:.|\n){0,20}?[:=-]?\s*(\d+\.?\d*)', 10),
        (r'(?i)(?:Total\s*Units?)(?:.|\n){0,20}?[:=-]?\s*(\d+\.?\d*)', 10),
        
        # OCR errors - common misreads of "Total Unit"
        (r'(?i)(?:Total\s*Writ|Fetal\s*Unit|Total\s*Wnit)(?:.|\n){0,20}?[:=-]?\s*(\d+\.?\d*)', 9),
        (r'(?i)(?:Tetal\s*Unit|Totel\s*Unit|Totai\s*Unit)(?:.|\n){0,20}?[:=-]?\s*(\d+\.?\d*)', 9),
        
        # Generic Consumption (medium priority)
        (r'(?i)(?:Consumption)(?:.|\n){0,30}?[:=-]?\s*(\d+\.?\d*)', 6),
        
        # OCR errors - common misreads of "Units"
        (r'(?i)(?:Wits|Wnits|Urits|Unifs)(?:.|\n){0,10}?[:=-]?\s*(\d+\.?\d*)', 5),
        
        # Units with measurement suffix (lower priority to avoid billing amounts)
        (r'(\d+\.?\d*)\s*(?:kWh|KWH|kwh)', 4),
        (r'(\d+\.?\d*)\s*(?:KL|kl|Kl)', 4),
        (r'(\d+\.?\d*)\s*(?:Units|units|UNITS)', 3),
        
        # Difference calculation pattern (common in Indian bills)
        (r'(?i)(?:Difference|Diff)(?:.|\n){0,20}?[:=-]?\s*(\d+\.?\d*)', 2),
        
        # Generic "Units" label (lowest priority)
        (r'(?i)(?:Units)(?:.|\n){0,15}?[:=-]?\s*(\d+\.?\d*)', 1),
    ]
    
    potential_units = []
    for pattern, priority in units_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            try:
                val = float(match.group(1))
                # Sanity check: units typically between 1-100000
                if 1 <= val <= 100000:
                    potential_units.append((val, priority))
                    print(f"OCR: Found units (priority {priority}): {val}")
            except (ValueError, IndexError):
                continue
    
    # DECISION LOGIC: Prefer calculated units if available and reasonable
    if calculated_units and 1 <= calculated_units <= 100000:
        # Use calculated units (highest reliability)
        data["units"] = calculated_units
        print(f"OCR: Selected CALCULATED units: {calculated_units}")
    elif potential_units:
        # Use extracted units if calculation not available
        sorted_units = sorted(potential_units, key=lambda x: (x[1], x[0]), reverse=True)
        data["units"] = sorted_units[0][0]
        print(f"OCR: Selected EXTRACTED units: {data['units']} (priority: {sorted_units[0][1]})")
    else:
        print("OCR: No valid units found in bill")

    # --- 2. PRODUCTION-GRADE AMOUNT PARSING ---
    # Context-aware extraction with priority for total bill amounts
    
    # Amount patterns with context (higher priority for bill totals)
    # Updated to handle comma separators (1,066.18) and spaces (890. 18)
    amount_patterns = [
        # Highest priority - explicit bill/total amounts (with comma handling)
        (r'(?i)(?:Bill\s*A[mn]ou?nt|A[mn]ou?nt\s*Payable)(?:.|\n){0,30}?₹?\s*([\d,]+\.?\d{0,2})', 10),
        (r'(?i)(?:Total\s*A[mn]ou?nt|Net\s*A[mn]ou?nt)(?:.|\n){0,30}?₹?\s*([\d,]+\.?\d{0,2})', 10),
        (r'(?i)(?:Total\s*Payable|Amount\s*Due)(?:.|\n){0,30}?₹?\s*([\d,]+\.?\d{0,2})', 10),
        (r'(?i)(?:Current\s*Bill)(?:.|\n){0,30}?₹?\s*([\d,]+\.?\d{0,2})', 10),
        (r'(?i)(?:Grand\s*Total|Final\s*Amount)(?:.|\n){0,30}?₹?\s*([\d,]+\.?\d{0,2})', 9),
        
        # Medium priority - generic amount labels
        (r'(?i)(?:Total)(?:.|\n){0,20}?[:=-]?\s*₹?\s*([\d,]+\.?\d{0,2})', 6),
        (r'(?i)(?:Payable)(?:.|\n){0,20}?[:=-]?\s*₹?\s*([\d,]+\.?\d{0,2})', 6),
        (r'(?i)(?:Amount)(?:.|\n){0,15}?[:=-]?\s*₹?\s*([\d,]+\.?\d{0,2})', 5),
        
        # Lower priority - standalone amounts with rupee symbol
        (r'₹\s*([\d,]+\.?\d{0,2})\b', 3),
    ]
    
    potential_amounts = []
    for pattern, priority in amount_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            amount_str = match.group(1)
            # Remove commas and spaces from amount string
            amount_str = amount_str.replace(',', '').replace(' ', '')
            try:
                val = float(amount_str)
                # Sanity checks for valid bill amounts
                if 50 <= val <= 1000000:  # Min ₹50, Max ₹10 lakhs
                    potential_amounts.append((val, priority, pattern[:40]))
                    print(f"OCR: Found amount (priority {priority}): ₹{val}")
            except ValueError:
                continue
    
    # Select amount with highest priority, then highest value
    if potential_amounts:
        # Sort by priority (descending), then by amount value (descending)
        sorted_amounts = sorted(potential_amounts, key=lambda x: (x[1], x[0]), reverse=True)
        data["amount"] = sorted_amounts[0][0]
        print(f"OCR: Selected amount: ₹{data['amount']} (priority: {sorted_amounts[0][1]})")
        
        # Log if multiple amounts found
        if len(sorted_amounts) > 1:
            print(f"OCR: Found {len(sorted_amounts)} amounts, selected highest priority")
    else:
        # Fallback: Try to calculate total from individual charges
        print("OCR: No direct total found, attempting to sum individual charges...")
        charge_patterns = [
            r'(?i)(?:Energy|Fixed|Customer|Electricity)\s*Charges?\s*(\d+\.?\d{0,2})',
            r'(?i)(?:Duty|Interest|Surcharge|FSA|FCA)\s*(?:Charges?)?\s*(\d+\.?\d{0,2})',
        ]
        charges = []
        for pattern in charge_patterns:
            for match in re.finditer(pattern, text):
                try:
                    val = float(match.group(1))
                    if val > 0:
                        charges.append(val)
                        print(f"OCR: Found charge: ₹{val}")
                except ValueError:
                    continue
        
        if charges:
            total = sum(charges)
            if total >= 50:
                data["amount"] = total
                print(f"OCR: Calculated total from {len(charges)} charges: ₹{total}")
        else:
            print("OCR: No valid amount found in bill")
    
    # --- 3. ENHANCED DATE PARSING ---
    # Extract ALL potential dates from the text
    date_patterns = [
        # Context-aware patterns (look for dates near keywords)
        (r'(?i)(?:Bill\s*Date|Invoice\s*Date)(?:.|\n){0,20}?(\d{2}[-/\.]\d{2}[-/\.]\d{2,4})', 10),
        (r'(?i)(?:Present|Current)(?:.|\n){0,20}?(\d{2}[-/\.]\d{2}[-/\.]\d{2,4})', 8),
        (r'(?i)(?:Date)(?:.|\n){0,10}?[:=]?\s*(\d{2}[-/\.]\d{2}[-/\.]\d{2,4})', 6),
        # General patterns (no context)
        (r'\b(\d{2}[-/\.]\d{2}[-/\.]\d{4})\b', 3),  # DD/MM/YYYY
        (r'\b(\d{2}[-/\.]\d{2}[-/\.]\d{2})\b', 2),   # DD/MM/YY
        (r'\b(\d{4}[-/\.]\d{2}[-/\.]\d{2})\b', 1),   # YYYY-MM-DD
    ]
    
    potential_dates = []
    for pattern, priority in date_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            date_str = match.group(1)
            # Validate and normalize the date
            normalized = validate_and_normalize_date(date_str, uploaded_date)
            if normalized:
                potential_dates.append((normalized, priority))
                print(f"OCR: Found date (priority {priority}): {date_str} -> {normalized}")
    
    # Select date with highest priority, then most recent
    if potential_dates:
        sorted_dates = sorted(potential_dates, key=lambda x: (x[1], x[0]), reverse=True)
        data["date"] = sorted_dates[0][0]
        print(f"OCR: Selected date: {data['date']} (priority: {sorted_dates[0][1]})")
    else:
        # Fallback to uploaded date
        if uploaded_date:
            if isinstance(uploaded_date, str):
                data["date"] = uploaded_date
            elif isinstance(uploaded_date, (datetime, date)):
                data["date"] = uploaded_date.strftime("%Y-%m-%d")
            print(f"OCR: No valid date found, using uploaded date: {data['date']}")
        else:
            print("OCR: No valid date found and no uploaded date provided")
        
    return data
