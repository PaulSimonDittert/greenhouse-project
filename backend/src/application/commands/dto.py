import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommandRequestDto(BaseModel):
    command_type: str
    device_id: uuid.UUID
    payload: dict = Field(default_factory=dict)


class CommandResultDto(BaseModel):
    status: str
    error_message: str | None = None


class CommandLogDto(BaseModel):
    id: uuid.UUID
    command_type: str
    device_id: uuid.UUID
    payload: dict | None = None
    status: str
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
