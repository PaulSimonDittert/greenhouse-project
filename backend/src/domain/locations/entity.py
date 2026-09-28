import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class Zone:
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict | None = None
    id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None

@dataclass(frozen=True)
class Location:
    name: str
    id: uuid.UUID | None = None

@dataclass(frozen=True)
class LocationConfig:
    location: Location
    zones: tuple[Zone, ...]