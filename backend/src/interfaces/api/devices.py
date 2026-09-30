import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from infrastructure.db import get_db
from application.readings.dto import SamplingSettingsDto
from application.readings.sampling_service import DeviceSamplingService
from application.readings.service import DeviceNotFoundError
from application.devices.family_service import DeviceFamilyService
from application.devices.dto import DeviceDto
from application.devices.mappers import devices_to_dtos
from application.locations.dto import ZoneAssignDeviceDto
from application.locations.zone_assignment_service import ZoneAssignmentService

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

@router.patch("/{device_id}/zone", status_code=200)
def assign_device_zone(device_id: uuid.UUID, payload: ZoneAssignDeviceDto, db: Session = Depends(get_db)):
    service = ZoneAssignmentService(db)
    try:
        service.assign(device_id, payload.zone_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{device_id}/sampling", response_model=SamplingSettingsDto)
def update_device_sampling(
    device_id: uuid.UUID,
    payload: SamplingSettingsDto,
    db: Session = Depends(get_db),
):
    service = DeviceSamplingService(db)
    try:
        return service.update_settings(
            device_id,
            payload.sampling_interval_seconds,
            payload.tracking_enabled,
        )
    except DeviceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error