import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class LocationAutomationContext:
    location_id: uuid.UUID
    zone_id: uuid.UUID
    moisture: float | None
    moisture_threshold_low: float
    moisture_threshold_high: float
    light: float | None = None
