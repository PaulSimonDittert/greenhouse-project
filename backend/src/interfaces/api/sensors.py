import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from infrastructure.db import get_db
from application.readings.dto import ReadingDto
from application.readings.service import DeviceNotFoundError, ReadingIngest
from application.sensors.service import SensorService

router = APIRouter(prefix="/api/sensors", tags=["sensors"])

class SensorCreate(BaseModel):
    type: str
    display_name: str | None = None

class SensorResponse(BaseModel):
    id: uuid.UUID
    device_type: str
    display_name: str | None
    default_config: dict
    sampling_interval_seconds: int
    tracking_enabled: bool

@router.post("", response_model=SensorResponse, status_code=201)
def create_sensor(payload: SensorCreate, db: Session = Depends(get_db)):
    service = SensorService(db)
    try:
        return service.create_sensor(payload.type, payload.display_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[SensorResponse])
def list_sensors(db: Session = Depends(get_db)):
    service = SensorService(db)
    return service.list_sensors()


@router.post("/{device_id}/read", response_model=ReadingDto, status_code=201)
def read_sensor(device_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ReadingIngest(db)
    try:
        return service.take_reading(device_id)
    except DeviceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{device_id}/readings", response_model=list[ReadingDto])
def list_sensor_readings(device_id: uuid.UUID, limit: int = 20, db: Session = Depends(get_db)):
    service = ReadingIngest(db)
    try:
        return service.list_readings(device_id, limit)
    except DeviceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error