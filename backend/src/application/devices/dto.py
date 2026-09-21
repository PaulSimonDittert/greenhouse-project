import uuid
from pydantic import BaseModel

class DeviceDto(BaseModel):
    id: uuid.UUID
    device_type: str
    role: str
    device_family: str
    display_name: str | None
    default_config: dict