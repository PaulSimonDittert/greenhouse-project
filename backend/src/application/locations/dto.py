import uuid
from pydantic import BaseModel

class ZoneCreateDto(BaseModel):
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict | None = None

class BuildLocationConfigRequestDto(BaseModel):
    location_name: str
    zones: list[ZoneCreateDto]

class ZoneUpdateDto(BaseModel):
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict | None = None

class ZoneAssignDeviceDto(BaseModel):
    zone_id: uuid.UUID | None


class LocationDto(BaseModel):
    id: uuid.UUID
    name: str

class ZoneDto(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict | None

class LocationConfigDto(BaseModel):
    location: LocationDto
    zones: list[ZoneDto]