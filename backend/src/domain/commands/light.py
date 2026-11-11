import uuid
from typing import Any

from domain.actuators.ports import ActuatorPort
from domain.commands.base import Command


class SetLightLevelCommand(Command):
    command_type = "set_light_level"
    target_state = None

    def __init__(self, device_id: uuid.UUID, payload: dict[str, Any] | None = None) -> None:
        super().__init__(device_id, payload)

    def execute(self, port: ActuatorPort) -> None:
        port.apply(self.device_id, self.command_type, self.payload)
