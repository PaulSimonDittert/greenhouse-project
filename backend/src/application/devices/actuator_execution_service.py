import uuid

from sqlalchemy.orm import Session

from application.devices.dto import ActuatorApplyResultDto, ActuatorExecutionDto
from domain.devices.entity import Device
from infrastructure.adapters.actuators.logging_decorator import LoggingActuatorDecorator
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
    MaxRunTimeExceededError,
)
from infrastructure.adapters.actuators.simulation import SimulationActuatorAdapter
from infrastructure.persistence.actuator_state_repository import ActuatorStateRepository
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.execution_log_repository import (
    ActuatorExecutionLogRepository,
)


class ActuatorDeviceNotFoundError(LookupError):
    pass


class ActuatorExecutionService:
    def __init__(self, db: Session):
        self._devices = DeviceRepository(db)
        self._states = ActuatorStateRepository(db)
        self._executions = ActuatorExecutionLogRepository(db)

    def list_recent(self, limit: int) -> list[ActuatorExecutionDto]:
        rows = self._executions.list_recent(limit)
        return [ActuatorExecutionDto.model_validate(row) for row in rows]

    def apply(
        self,
        device_id: uuid.UUID,
        command: str,
        payload: dict,
    ) -> ActuatorApplyResultDto:
        device: Device | None = self._devices.get_device(device_id)
        if device is None:
            raise ActuatorDeviceNotFoundError(f"Device {device_id} not found")
        if device.role != "actuator":
            raise ValueError(f"Device {device_id} is not an actuator")

        actuator: SimulationActuatorAdapter = SimulationActuatorAdapter()
        max_runtime: MaxRunTimeActuatorDecorator = MaxRunTimeActuatorDecorator(
            actuator,
            self._states,
        )
        decorated_actuator: LoggingActuatorDecorator = LoggingActuatorDecorator(
            max_runtime,
            self._executions,
        )
        try:
            decorated_actuator.apply(device_id, command, payload)
        except MaxRunTimeExceededError as error:
            return ActuatorApplyResultDto(
                success=False,
                policy_applied=[*error.policy_applied, "logging"],
                message=error.message,
            )

        return ActuatorApplyResultDto(
            success=True,
            policy_applied=["logging"],
            message=None,
        )
