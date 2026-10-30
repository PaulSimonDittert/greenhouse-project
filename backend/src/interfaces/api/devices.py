import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from application.devices.actuator_state_service import ActuatorNotFoundError, ActuatorStateService
from application.devices.dto import DeviceDto, DeviceTransitionDto
from application.devices.family_service import DeviceFamilyService
from application.devices.mappers import device_to_dto, devices_to_dtos
from application.locations.dto import ZoneAssignDeviceDto
from application.locations.zone_assignment_service import ZoneAssignmentService
from application.readings.dto import SamplingSettingsDto
from application.readings.sampling_service import DeviceSamplingService
from application.readings.service import DeviceNotFoundError
from infrastructure.db import get_db
from infrastructure.persistence.actuator_state_repository import ActuatorStateRepository

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.post("/provision", response_model=list[DeviceDto], status_code=201)
def provision_family(family: str = Query(...), db: Session = Depends(get_db)):
    service = DeviceFamilyService(db)
    try:
        devices = service.provision_family(family)
        state_repo = ActuatorStateRepository(db)
        states = state_repo.list_for_devices([d.id for d in devices if d.id is not None and d.role == "actuator"])
        return devices_to_dtos(devices, states)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[DeviceDto])
def list_devices(
    family: str | None = Query(None),
    role: str | None = Query(None),
    db: Session = Depends(get_db),
):
    service = DeviceFamilyService(db)
    devices = service.list_devices(device_family=family, role=role)
    actuator_ids = [d.id for d in devices if d.id is not None and d.role == "actuator"]
    states = ActuatorStateRepository(db).list_for_devices(actuator_ids)
    return devices_to_dtos(devices, states)


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


@router.post("/{device_id}/transition", response_model=DeviceDto)
def transition_actuator(device_id: uuid.UUID, payload: DeviceTransitionDto, db: Session = Depends(get_db)):
    service = ActuatorStateService(db)
    try:
        new_state = service.transition(device_id, payload.target)
    except ActuatorNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    device = service._devices.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    return device_to_dto(device, state=new_state)
