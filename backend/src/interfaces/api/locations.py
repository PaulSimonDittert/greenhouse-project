import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from infrastructure.db import get_db
from domain.locations.errors import ConfigurationError
from application.locations.dto import (
    BuildLocationConfigRequestDto, LocationDto, ZoneDto, LocationConfigDto,
    ZoneCreateDto, ZoneUpdateDto
)
from application.locations.mappers import (
    location_config_to_dto, location_row_to_dto, zone_row_to_dto
)
from application.locations.config_service import LocationConfigService
from application.locations.zone_assignment_service import ZoneAssignmentService
from infrastructure.persistence.location_repository import LocationRepository
from application.devices.dto import DeviceDto

router = APIRouter(prefix="/api/locations", tags=["locations"])

@router.post("/config", response_model=LocationConfigDto, status_code=status.HTTP_201_CREATED)
def create_location_config(request: BuildLocationConfigRequestDto, db: Session = Depends(get_db)):
    service = LocationConfigService(db)
    try:
        loc_row, zone_rows = service.build_and_save(request)
        return location_config_to_dto(loc_row, zone_rows)
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[LocationDto])
def list_locations(db: Session = Depends(get_db)):
    service = LocationConfigService(db)
    return [location_row_to_dto(loc) for loc in service.list_locations()]

@router.get("/{location_id}/config", response_model=LocationConfigDto)
def get_location_config(location_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = LocationRepository(db)
    config = repo.get_config(location_id)
    if not config:
        raise HTTPException(status_code=404, detail="Location not found")
    return location_config_to_dto(config[0], config[1])

@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: uuid.UUID, db: Session = Depends(get_db)):
    service = LocationConfigService(db)
    if not service.delete_location(location_id):
        raise HTTPException(status_code=404, detail="Location not found")

@router.post("/{location_id}/zones", response_model=ZoneDto, status_code=status.HTTP_201_CREATED)
def add_zone(location_id: uuid.UUID, payload: ZoneCreateDto, db: Session = Depends(get_db)):
    service = LocationConfigService(db)
    try:
        z_row = service.add_zone(location_id, payload.name, payload.moisture_threshold_low, payload.moisture_threshold_high, payload.schedule)
        return zone_row_to_dto(z_row)
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{location_id}/zones/{zone_id}", response_model=ZoneDto)
def update_zone(location_id: uuid.UUID, zone_id: uuid.UUID, payload: ZoneUpdateDto, db: Session = Depends(get_db)):
    service = LocationConfigService(db)
    try:
        z_row = service.update_zone(location_id, zone_id, payload.name, payload.moisture_threshold_low, payload.moisture_threshold_high, payload.schedule)
        return zone_row_to_dto(z_row)
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{location_id}/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(location_id: uuid.UUID, zone_id: uuid.UUID, db: Session = Depends(get_db)):
    service = LocationConfigService(db)
    try:
        service.delete_zone(location_id, zone_id)
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{location_id}/zones/{zone_id}/devices", response_model=list[DeviceDto])
def list_zone_devices(location_id: uuid.UUID, zone_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ZoneAssignmentService(db)
    try:
        device_rows = service.list_devices(location_id, zone_id)
        return [
            DeviceDto(
                id=row.id, device_type=row.device_type, role=row.role,
                device_family=row.device_family, display_name=row.display_name,
                default_config=row.default_config
            ) for row in device_rows
        ]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))