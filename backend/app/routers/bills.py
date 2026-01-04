from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from app.models.models import Bill, User
from app.schemas.schemas import BillResponse
from app.routers.deps import get_current_user
from app.services.ocr_service import extract_text_from_image, parse_bill_data
import shutil
import os
import uuid
from datetime import date, datetime

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
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1] if file.filename else "jpg"
    file_path = f"{UPLOAD_DIR}/{file_id}.{extension}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Run OCR
    try:
        text = extract_text_from_image(file_path)
        parsed_data = parse_bill_data(text)
        
        # Validation
        units = parsed_data.get("units", 0)
        amount = parsed_data.get("amount", 0)
        
        if units == 0 and amount == 0:
             if os.path.exists(file_path):
                 os.remove(file_path)
                 
             raise HTTPException(
                status_code=400, 
                detail="OCR Failed: Unable to read 'Units' or 'Amount' from the image."
            )

        # Parse date
        final_date = date.today()
        parsed_date_str = parsed_data.get("date")
        if parsed_date_str:
            try:
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"]:
                    try:
                        final_date = datetime.strptime(parsed_date_str, fmt).date()
                        break
                    except ValueError:
                        continue
            except Exception:
                final_date = date.today()
        
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
