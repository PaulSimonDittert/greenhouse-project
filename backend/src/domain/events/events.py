import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReadingCreated:
    device_id: uuid.UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime
    location_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None

    @property
    def event_type(self) -> str:
        return "reading.created"


@dataclass(frozen=True)
class ThresholdCrossed:
    device_id: uuid.UUID | None
    value: float
    threshold: float
    location_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None
    severity: str = "warning"
    message: str | None = None

    @property
    def event_type(self) -> str:
        return "threshold.crossed"


@dataclass(frozen=True)
class CommandSucceeded:
    command_type: str
    device_id: uuid.UUID
    location_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None

    @property
    def event_type(self) -> str:
        return "command.succeeded"


@dataclass(frozen=True)
class CommandFailed:
    command_type: str
    device_id: uuid.UUID | None
    error_message: str | None = None
    location_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None

    @property
    def event_type(self) -> str:
        return "command.failed"


@dataclass(frozen=True)
class ActuatorStateChanged:
    device_id: uuid.UUID
    previous_state: str
    current_state: str
    location_id: uuid.UUID | None = None
    zone_id: uuid.UUID | None = None
    command_type: str | None = None

    @property
    def event_type(self) -> str:
        return "actuator.state.changed"
