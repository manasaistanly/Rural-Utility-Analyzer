from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from app.models.models import Bill, User
from app.schemas.schemas import BillResponse
from app.routers.deps import get_current_user
from app.services.ocr_service import extract_text_from_image, parse_bill_data
import shutil
import os
import uuid
from datetime import date, datetime, timedelta
import random

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=BillResponse)
async def upload_bill(
    file: UploadFile = File(...),
    bill_type: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    # Save file
    print(f"DEBUG: Start upload for {file.filename}")
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1] if file.filename else "jpg"
    file_path = f"{UPLOAD_DIR}/{file_id}.{extension}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"DEBUG: File saved to {file_path}")
        
    # Run OCR
    try:
        print("DEBUG: Starting OCR extraction...")
        text = extract_text_from_image(file_path)
        print(f"DEBUG: OCR finished. Text First 100 chars: {text[:100]}")
        
        # Pass current date as fallback for missing dates
        current_date = date.today()
        parsed_data = parse_bill_data(text, uploaded_date=current_date)
        print(f"DEBUG: Data parsed: {parsed_data}")
        
        # Validation - just log if OCR failed, but don't block upload
        units = parsed_data.get("units", 0)
        amount = parsed_data.get("amount", 0)
        
        if units == 0 and amount == 0:
            print(f"WARNING: OCR extracted zero values for file {file_path}. User may need to manually verify.")

        # Get the parsed date (already validated and normalized by parse_bill_data)
        final_date = None
        parsed_date_str = parsed_data.get("date")
        
        if parsed_date_str:
            try:
                # parse_bill_data returns dates in YYYY-MM-DD format
                final_date = datetime.strptime(parsed_date_str, "%Y-%m-%d").date()
                print(f"DEBUG: Using extracted date: {final_date}")
            except Exception as e:
                print(f"WARNING: Failed to parse date {parsed_date_str}: {e}")
        
        # If still no date, use uploaded date (current date)
        if final_date is None:
            final_date = current_date
            print(f"DEBUG: No valid date extracted, using uploaded date: {final_date}")
        
        # Create Bill document
        new_bill = Bill(
            user_id=str(current_user.id),
            bill_type=bill_type,
            image_path=file_path,
            units_consumed=units,
            total_amount=amount,
            bill_date=final_date,
            is_verified=True
        )
        await new_bill.insert()
        
        return BillResponse(
            id=str(new_bill.id),
            user_id=str(new_bill.user_id),
            bill_type=new_bill.bill_type,
            image_path=new_bill.image_path,
            units_consumed=new_bill.units_consumed,
            total_amount=new_bill.total_amount,
            bill_date=new_bill.bill_date,
            is_verified=new_bill.is_verified,
            uploaded_at=new_bill.uploaded_at
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"UPLOAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/", response_model=List[BillResponse])
async def get_bills(current_user: User = Depends(get_current_user)):
    bills = await Bill.find(Bill.user_id == str(current_user.id)).to_list()
    return [
        BillResponse(
            id=str(bill.id),
            user_id=str(bill.user_id),
            bill_type=bill.bill_type,
            image_path=bill.image_path,
            units_consumed=bill.units_consumed,
            total_amount=bill.total_amount,
            bill_date=bill.bill_date,
            is_verified=bill.is_verified,
            uploaded_at=bill.uploaded_at
        )
        for bill in bills
    ]

@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(bill_id: str, current_user: User = Depends(get_current_user)):
    from beanie import PydanticObjectId
    
    bill = await Bill.get(PydanticObjectId(bill_id))
    if not bill or bill.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Bill not found")
    
    return BillResponse(
        id=str(bill.id),
        user_id=str(bill.user_id),
        bill_type=bill.bill_type,
        image_path=bill.image_path,
        units_consumed=bill.units_consumed,
        total_amount=bill.total_amount,
        bill_date=bill.bill_date,
        is_verified=bill.is_verified,
        uploaded_at=bill.uploaded_at
    )
