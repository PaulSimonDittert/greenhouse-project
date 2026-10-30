import uuid

from pydantic import BaseModel, Field


class DeviceTransitionDto(BaseModel):
    target: str


class DeviceDto(BaseModel):
    id: uuid.UUID
    device_type: str
    role: str
    device_family: str
    display_name: str | None
    default_config: dict
    zone_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
    state: str = "idle"
    allowed_commands: list[str] = Field(default_factory=list)