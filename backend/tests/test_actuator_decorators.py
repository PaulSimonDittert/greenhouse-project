import uuid
from datetime import UTC, datetime, timedelta

import pytest

from infrastructure.adapters.actuators.logging_decorator import LoggingActuatorDecorator
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
    MaxRunTimeExceededError,
)


class FakeInnerAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[uuid.UUID, str, dict]] = []
        self.error: Exception | None = None

    def apply(self, device_id: uuid.UUID, command: str, payload: dict) -> None:
        if self.error is not None:
            raise self.error
        self.calls.append((device_id, command, payload.copy()))


class FakeExecutionLogRepository:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def insert(self, *, device_id: uuid.UUID, success: bool, policy_applied: list[str], message: str | None = None) -> dict:
        row = {
            "device_id": device_id,
            "success": success,
            "policy_applied": list(policy_applied),
            "message": message,
        }
        self.rows.append(row)
        return row


class FakeActuatorStateRow:
    def __init__(self, state: str, updated_at: datetime) -> None:
        self.state = state
        self.updated_at = updated_at


class FakeActuatorStateRepository:
    def __init__(self, row: FakeActuatorStateRow | None) -> None:
        self.row = row

    def get_row(self, device_id: uuid.UUID) -> FakeActuatorStateRow | None:
        return self.row


def test_max_runtime_does_not_call_inner() -> None:
    device_id = uuid.uuid4()
    inner = FakeInnerAdapter()
    stale_row = FakeActuatorStateRow(
        "running",
        datetime.now(UTC) - timedelta(minutes=45),
    )
    state_repository = FakeActuatorStateRepository(stale_row)
    decorator = MaxRunTimeActuatorDecorator(inner, state_repository)

    with pytest.raises(MaxRunTimeExceededError, match="Max run time exceeded"):
        decorator.apply(device_id, "start_pump", {"mode": "manual"})

    assert inner.calls == []


def test_failed_policy_writes_execution_row() -> None:
    device_id = uuid.uuid4()
    inner = FakeInnerAdapter()
    stale_row = FakeActuatorStateRow(
        "running",
        datetime.now(UTC) - timedelta(minutes=45),
    )
    state_repository = FakeActuatorStateRepository(stale_row)
    execution_log_repository = FakeExecutionLogRepository()
    decorator = LoggingActuatorDecorator(
        MaxRunTimeActuatorDecorator(inner, state_repository),
        execution_log_repository,
    )

    with pytest.raises(MaxRunTimeExceededError, match="Max run time exceeded"):
        decorator.apply(device_id, "start_pump", {"mode": "manual"})

    assert execution_log_repository.rows[-1] == {
        "device_id": device_id,
        "success": False,
        "policy_applied": ["maxRunTime", "logging"],
        "message": "Max run time exceeded",
    }
    assert inner.calls == []


def test_logging_records_success_and_forwards_command() -> None:
    device_id = uuid.uuid4()
    payload = {"mode": "manual"}
    inner = FakeInnerAdapter()
    execution_log_repository = FakeExecutionLogRepository()
    decorator = LoggingActuatorDecorator(inner, execution_log_repository)

    decorator.apply(device_id, "unknown_command", payload)

    assert inner.calls == [(device_id, "unknown_command", payload)]
    assert execution_log_repository.rows == [
        {
            "device_id": device_id,
            "success": True,
            "policy_applied": ["logging"],
            "message": None,
        }
    ]


def test_logging_records_inner_failure_and_reraises() -> None:
    device_id = uuid.uuid4()
    inner = FakeInnerAdapter()
    inner.error = RuntimeError("Adapter failed")
    execution_log_repository = FakeExecutionLogRepository()
    decorator = LoggingActuatorDecorator(inner, execution_log_repository)

    with pytest.raises(RuntimeError, match="Adapter failed"):
        decorator.apply(device_id, "start_pump", {})

    assert execution_log_repository.rows == [
        {
            "device_id": device_id,
            "success": False,
            "policy_applied": ["logging"],
            "message": "Adapter failed",
        }
    ]
