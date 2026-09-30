import uuid
from datetime import datetime

from pydantic import BaseModel


class ReadingDto(BaseModel):
    device_id: uuid.UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime


class SamplingSettingsDto(BaseModel):
    sampling_interval_seconds: int
    tracking_enabled: bool