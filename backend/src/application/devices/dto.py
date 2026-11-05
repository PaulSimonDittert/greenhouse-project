import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class ActuatorApplyRequest(BaseModel):
    command: str
    payload: dict = Field(default_factory=dict)


class ActuatorApplyResultDto(BaseModel):
    success: bool
    policy_applied: list[str]
    message: str | None


class ActuatorExecutionDto(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    success: bool
    policy_applied: list[str]
    message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)