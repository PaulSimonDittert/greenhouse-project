import uuid
from typing import Any

from domain.actuators.ports import ActuatorPort
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeExceededError,
)
from infrastructure.persistence.execution_log_repository import (
    ActuatorExecutionLogRepository,
)


class LoggingActuatorDecorator(ActuatorPort):
    def __init__(
        self,
        inner: ActuatorPort,
        execution_log_repository: ActuatorExecutionLogRepository,
    ) -> None:
        self.inner = inner
        self.execution_log_repository = execution_log_repository

    def apply(self, device_id: uuid.UUID, command: str, payload: dict[str, Any]) -> None:
        try:
            self.inner.apply(device_id, command, payload)
        except MaxRunTimeExceededError as exc:
            self.execution_log_repository.insert(
                device_id=device_id,
                success=False,
                policy_applied=[*exc.policy_applied, "logging"],
                message=exc.message,
            )
            raise
        except Exception as exc:
            message = str(exc) or "Actuator apply failed"
            self.execution_log_repository.insert(
                device_id=device_id,
                success=False,
                policy_applied=["logging"],
                message=message,
            )
            raise

        self.execution_log_repository.insert(
            device_id=device_id,
            success=True,
            policy_applied=["logging"],
            message=None,
        )
