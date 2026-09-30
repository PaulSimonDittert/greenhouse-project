from copy import deepcopy
from dataclasses import dataclass
from typing import Any
import uuid

from domain.actuators.ports import ActuatorPort


@dataclass(frozen=True)
class AppliedCommand:
    device_id: uuid.UUID
    command: str
    payload: dict[str, Any]


class SimulationActuatorAdapter(ActuatorPort):
    def __init__(self) -> None:
        self.applied_commands: list[AppliedCommand] = []

    def apply(self, device_id: uuid.UUID, command: str, payload: dict[str, Any]) -> None:
        self.applied_commands.append(
            AppliedCommand(device_id=device_id, command=command, payload=deepcopy(payload))
        )