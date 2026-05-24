import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from models.guest import GuestUser, GuestPreference
from database import get_db
from schemas import GuestCreateRequest, GuestPreferenceUpdate, GuestResponse, GuestPreferenceCreate

router = APIRouter()

@router.post("/", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
def create_guest(
    data: GuestCreateRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    guest_uid = str(uuid.uuid4())[:10]
    guest = GuestUser(
        guest_uid=guest_uid,
        ip_address=request.client.host,
        device_id=data.device_id,
        device_name=data.device_name,
        android_version=data.android_version,
        app_version=data.app_version,
        app_version_code=data.app_version_code,
        state_id=data.state_id,
        district_id=data.district_id,
        city_id=data.city_id
    )
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest

@router.post("/guest/preferences")
def create_guest_preference(data: GuestPreferenceCreate, db: Session = Depends(get_db)):
    # Check if preference already exists
    existing = db.query(GuestPreference).filter(GuestPreference.guest_uid == data.guest_uid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Guest preference already exists")
    
    preference = GuestPreference(
        guest_uid=data.guest_uid,
        language=data.language,
        state_id=data.state_id,
        district_id=data.district_id,
        city_id=data.city_id
    )
    
    db.add(preference)
    db.commit()
    db.refresh(preference)
    
    return {
        "message": "Guest preference created successfully",
        "data": {
            "guest_uid": preference.guest_uid,
            "language": preference.language,
            "state": preference.state.name if preference.state else None,
            "district": preference.district.name if preference.district else None,
            "city": preference.city.name if preference.city else None
        }
    }
@router.put("/guest/preferences/{guest_uid}")
def update_guest_preference(guest_uid: str, data: GuestPreferenceUpdate, db: Session = Depends(get_db)):
    preference = db.query(GuestPreference).filter(GuestPreference.guest_uid == guest_uid).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Guest preference not found")
    
    if data.language is not None:
        preference.language = data.language
    if data.state_id is not None:
        preference.state_id = data.state_id
    if data.district_id is not None:
        preference.district_id = data.district_id
    if data.city_id is not None:
        preference.city_id = data.city_id
    
    db.commit()
    db.refresh(preference)
    
    return {
        "message": "Guest preference updated successfully",
        "data": {
            "guest_uid": preference.guest_uid,
            "language": preference.language,
            "state": preference.state.name if preference.state else None,
            "district": preference.district.name if preference.district else None,
            "city": preference.city.name if preference.city else None
        }
    }
