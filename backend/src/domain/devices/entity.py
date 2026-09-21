import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class Device:
    device_type: str
    role: str
    device_family: str
    display_name: str
    default_config: dict
    id: uuid.UUID | None = None