import uuid
from dataclasses import dataclass

@dataclass
class Sensor:
    device_type: str
    display_name: str | None
    default_config: dict
    id: uuid.UUID | None = None