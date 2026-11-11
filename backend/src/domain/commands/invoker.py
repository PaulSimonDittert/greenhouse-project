from __future__ import annotations

import uuid
from typing import Any

from domain.actuators.ports import ActuatorPort
from domain.commands.base import Command
from domain.commands.light import SetLightLevelCommand
from domain.commands.pump import StartPumpCommand, StopPumpCommand


class UnknownCommandError(ValueError):
    pass


COMMAND_REGISTRY: dict[str, type[Command]] = {
    StartPumpCommand.command_type: StartPumpCommand,
    StopPumpCommand.command_type: StopPumpCommand,
    SetLightLevelCommand.command_type: SetLightLevelCommand,
}


def command_for(command_type: str, device_id: uuid.UUID, payload: dict[str, Any] | None = None) -> Command:
    command_cls = COMMAND_REGISTRY.get(command_type)
    if command_cls is None:
        raise UnknownCommandError(f"Unknown command type: {command_type}")
    return command_cls(device_id=device_id, payload=payload)


class CommandInvoker:
    def run(self, command: Command, port: ActuatorPort) -> None:
        command.execute(port)
