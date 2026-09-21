from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from infrastructure.db import get_db
from application.devices.family_service import DeviceFamilyService
from application.devices.dto import DeviceDto
from application.devices.mappers import devices_to_dtos

router = APIRouter(prefix="/api/devices", tags=["devices"])

@router.post("/provision", response_model=list[DeviceDto], status_code=201)
def provision_family(family: str = Query(...), db: Session = Depends(get_db)):
    service = DeviceFamilyService(db)
    try:
        devices = service.provision_family(family)
        return devices_to_dtos(devices)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[DeviceDto])
def list_devices(
    family: str | None = Query(None), 
    role: str | None = Query(None), 
    db: Session = Depends(get_db)
):
    service = DeviceFamilyService(db)
    devices = service.list_devices(device_family=family, role=role)
    return devices_to_dtos(devices)