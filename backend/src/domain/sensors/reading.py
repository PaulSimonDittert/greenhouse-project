import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Reading:
    device_id: uuid.UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime