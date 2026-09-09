import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from infrastructure.db import get_db
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