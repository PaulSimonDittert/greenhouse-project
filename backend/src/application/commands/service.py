from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from domain.actuators.context import ActuatorContext
from domain.actuators.ports import ActuatorPort
from domain.commands.base import Command
from domain.commands.invoker import CommandInvoker, UnknownCommandError, command_for
from infrastructure.adapters.actuators.logging_decorator import LoggingActuatorDecorator
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
    MaxRunTimeExceededError,
)
from infrastructure.adapters.actuators.simulation import SimulationActuatorAdapter
from infrastructure.persistence.actuator_state_repository import ActuatorStateRepository
from infrastructure.persistence.command_log_repository import CommandLogRepository
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.execution_log_repository import ActuatorExecutionLogRepository


class DeviceNotFoundError(LookupError):
    pass


@dataclass
class CommandResult:
    status: str
    error_message: str | None = None


def build_actuator_port(
    db: Session,
    *,
    state_repository: ActuatorStateRepository | None = None,
    execution_log_repository: ActuatorExecutionLogRepository | None = None,
) -> ActuatorPort:
    state_repo = state_repository or ActuatorStateRepository(db)
    execution_repo = execution_log_repository or ActuatorExecutionLogRepository(db)
    inner = SimulationActuatorAdapter()
    protected = MaxRunTimeActuatorDecorator(inner, state_repo)
    return LoggingActuatorDecorator(protected, execution_repo)


class CommandService:
    def __init__(
        self,
        db: Session,
        *,
        devices: DeviceRepository | None = None,
        states: ActuatorStateRepository | None = None,
        executions: ActuatorExecutionLogRepository | None = None,
        command_log: CommandLogRepository | None = None,
    ) -> None:
        self.db = db
        self._devices = devices or DeviceRepository(db)
        self._states = states or ActuatorStateRepository(db)
        self._executions = executions or ActuatorExecutionLogRepository(db)
        self._command_log = command_log or CommandLogRepository(db)

    def execute(self, device_id: uuid.UUID, command_type: str, payload: dict[str, Any] | None = None) -> Any:
        device = self._devices.get_device(device_id)
        if device is None or device.role != "actuator":
            raise DeviceNotFoundError(f"Device {device_id} not found")

        current_state = self._states.get_for_device(device_id) or "idle"
        try:
            command = command_for(command_type, device_id, payload or {})
        except UnknownCommandError:
            raise

        if command_type not in ActuatorContext(current_state).allowed_commands:
            return self._command_log.insert(
                command_type=command_type,
                device_id=device_id,
                payload=payload or {},
                status="rejected",
                error_message=f"Command '{command_type}' is not allowed in state '{current_state}'.",
            )

        port = build_actuator_port(
            self.db,
            state_repository=self._states,
            execution_log_repository=self._executions,
        )
        invoker = CommandInvoker()

        try:
            invoker.run(command, port)
        except MaxRunTimeExceededError as exc:
            return self._command_log.insert(
                command_type=command_type,
                device_id=device_id,
                payload=payload or {},
                status="failed",
                error_message=exc.message,
            )
        except Exception as exc:  # pragma: no cover - defensive safety net
            return self._command_log.insert(
                command_type=command_type,
                device_id=device_id,
                payload=payload or {},
                status="failed",
                error_message=str(exc),
            )

        if command.target_state is not None and command.target_state != current_state:
            new_state = ActuatorContext(current_state).transition(command.target_state)
            self._states.save(device_id, new_state)

        return self._command_log.insert(
            command_type=command_type,
            device_id=device_id,
            payload=payload or {},
            status="success",
        )
