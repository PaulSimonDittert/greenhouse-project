from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

from domain.actuators.ports import ActuatorPort
from infrastructure.persistence.actuator_state_repository import ActuatorStateRepository


class MaxRunTimeExceededError(RuntimeError):
    def __init__(self, message: str = "Max run time exceeded", policy_applied: list[str] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.policy_applied = policy_applied or ["maxRunTime"]


class MaxRunTimeActuatorDecorator(ActuatorPort):
    def __init__(
        self,
        inner: ActuatorPort,
        state_repository: ActuatorStateRepository,
        *,
        timeout_minutes: int = 30,
    ) -> None:
        self.inner = inner
        self.state_repository = state_repository
        self.timeout_minutes = timeout_minutes

    def apply(self, device_id: uuid.UUID, command: str, payload: dict[str, Any]) -> None:
        row = self.state_repository.get_row(device_id)
        if row is not None and row.state == "running":
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.timeout_minutes)
            if row.updated_at <= cutoff:
                raise MaxRunTimeExceededError(
                    "Max run time exceeded",
                    ["maxRunTime"],
                )

        self.inner.apply(device_id, command, payload)
