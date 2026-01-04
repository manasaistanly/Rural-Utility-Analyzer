from app.services.ocr_service import parse_bill_data

def test_ocr():
    print("Testing OCR Logic...")
    
    # Test Case 1: Standard Electricity Bill
    text1 = """
    TELANGANA STATE SOUTHERN POWER DISTRIBUTION COMPANY LIMITED
    Bill No: 12345
    Date: 15/05/2025
    
    Units Billed: 250
    Rate: 5.00
    Net Amount: ₹1250.00
    """
    res1 = parse_bill_data(text1)
    print(f"Test 1 (Electricity): {res1}")
    assert res1['units'] == 250.0
    assert res1['amount'] == 1250.0
    
    # Test Case 2: Water Bill
    text2 = """
    HYDERABAD METROPOLITAN WATER SUPPLY & SEWERAGE BOARD
    Consumer No: 98765
    Bill Date: 12-04-2025
    
    Consumption (KL): 15.5
    Sewerage Cess: 35%
    Total Payable: 450.00
    """
    res2 = parse_bill_data(text2)
    print(f"Test 2 (Water): {res2}")
    assert res2['units'] == 15.5
    assert res2['amount'] == 450.0

    # Test Case 3: Messy/OCR Noise
    text3 = """
    Bill Date: 10/10/2025
    Unls Consumed: 180 .
    Am0unt Payable : 900.50
    """
    # My regex should catch "Consumed" and "Payable" even if noise exists nearby?
    # Actually my regex looks for "Units Consumed" or "Payable".
    # Let's see if "Payable" with "Am0unt" works.
    # The regex for amount includes r'(?i)(?:Payable).{0,15}? ...'
    
    res3 = parse_bill_data(text3)
    print(f"Test 3 (Messy): {res3}")
    assert res3['amount'] == 900.5
    
    print("\n✅ OCR Logic Verified!")

if __name__ == "__main__":
    test_ocr()
