import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from application.commands.service import CommandService
from domain.commands.invoker import UnknownCommandError
from domain.events.bus import EventBus
from domain.events.events import ActuatorStateChanged, CommandFailed, CommandSucceeded


class FakeDeviceRepository:
    def __init__(self, device):
        self.device = device

    def get_device(self, device_id):
        return self.device


class FakeStateRow:
    def __init__(self, state):
        self.state = state
        self.updated_at = datetime.now(UTC)


class FakeStateRepository:
    def __init__(self, state):
        self.state = state
        self.saved = []

    def get_for_device(self, device_id):
        return self.state

    def get_row(self, device_id):
        return FakeStateRow(self.state)

    def save(self, device_id, state):
        self.saved.append((device_id, state))
        self.state = state
        return state


class FakeExecutionLogRepository:
    def __init__(self):
        self.rows = []

    def insert(self, *, device_id, success, policy_applied, message=None):
        row = {
            "device_id": device_id,
            "success": success,
            "policy_applied": list(policy_applied),
            "message": message,
        }
        self.rows.append(row)
        return row


class FakeCommandLogRepository:
    def __init__(self):
        self.rows = []

    def insert(self, *, command_type, device_id, payload=None, status="success", error_message=None):
        row = {
            "command_type": command_type,
            "device_id": device_id,
            "payload": payload or {},
            "status": status,
            "error_message": error_message,
        }
        self.rows.append(row)
        return row


def test_illegal_command_rejected_logged():
    device_id = uuid.uuid4()
    state_repo = FakeStateRepository("running")
    command_log = FakeCommandLogRepository()
    service = CommandService(
        object(),
        devices=FakeDeviceRepository(SimpleNamespace(role="actuator", device_type="water_pump")),
        states=state_repo,
        executions=FakeExecutionLogRepository(),
        command_log=command_log,
        event_bus=EventBus(),
    )

    service.execute(device_id, "start_pump")

    assert command_log.rows[-1]["status"] == "rejected"
    assert state_repo.state == "running"


def test_start_pump_transitions_to_running():
    device_id = uuid.uuid4()
    state_repo = FakeStateRepository("idle")
    command_log = FakeCommandLogRepository()
    execution_log = FakeExecutionLogRepository()
    event_bus = EventBus()
    succeeded = []
    state_changes = []
    event_bus.subscribe(CommandSucceeded, succeeded.append)
    event_bus.subscribe(ActuatorStateChanged, state_changes.append)
    service = CommandService(
        object(),
        devices=FakeDeviceRepository(SimpleNamespace(role="actuator", device_type="water_pump")),
        states=state_repo,
        executions=execution_log,
        command_log=command_log,
        event_bus=event_bus,
    )

    service.execute(device_id, "start_pump", {"mode": "manual"})

    assert state_repo.state == "running"
    assert command_log.rows[-1]["status"] == "success"
    assert execution_log.rows[-1]["success"] is True
    assert len(succeeded) == 1
    assert succeeded[0].device_id == device_id
    assert succeeded[0].event_type == "command.succeeded"
    assert len(state_changes) == 1
    assert state_changes[0].previous_state == "idle"
    assert state_changes[0].current_state == "running"
    assert state_changes[0].command_type == "start_pump"


def test_set_light_level_succeeds_without_changing_running_state():
    device_id = uuid.uuid4()
    state_repo = FakeStateRepository("running")
    command_log = FakeCommandLogRepository()
    execution_log = FakeExecutionLogRepository()
    event_bus = EventBus()
    succeeded = []
    state_changes = []
    event_bus.subscribe(CommandSucceeded, succeeded.append)
    event_bus.subscribe(ActuatorStateChanged, state_changes.append)
    service = CommandService(
        object(),
        devices=FakeDeviceRepository(SimpleNamespace(role="actuator", device_type="grow_light")),
        states=state_repo,
        executions=execution_log,
        command_log=command_log,
        event_bus=event_bus,
    )

    service.execute(device_id, "set_light_level", {"level": 1})

    assert state_repo.state == "running"
    assert state_repo.saved == []
    assert command_log.rows[-1]["status"] == "success"
    assert execution_log.rows[-1]["success"] is True
    assert len(succeeded) == 1
    assert state_changes == []


def test_unknown_command_publishes_failure_event():
    device_id = uuid.uuid4()
    event_bus = EventBus()
    observed = []
    event_bus.subscribe(CommandFailed, observed.append)
    service = CommandService(
        object(),
        devices=FakeDeviceRepository(SimpleNamespace(role="actuator", device_type="water_pump")),
        states=FakeStateRepository("idle"),
        executions=FakeExecutionLogRepository(),
        command_log=FakeCommandLogRepository(),
        event_bus=event_bus,
    )

    with pytest.raises(UnknownCommandError):
        service.execute(device_id, "not_a_command")

    assert len(observed) == 1
    assert observed[0].device_id == device_id
    assert observed[0].error_message


def test_pump_command_is_rejected_for_grow_light():
    device_id = uuid.uuid4()
    state_repo = FakeStateRepository("idle")
    command_log = FakeCommandLogRepository()
    execution_log = FakeExecutionLogRepository()
    service = CommandService(
        object(),
        devices=FakeDeviceRepository(SimpleNamespace(role="actuator", device_type="grow_light")),
        states=state_repo,
        executions=execution_log,
        command_log=command_log,
        event_bus=EventBus(),
    )

    service.execute(device_id, "start_pump")

    assert command_log.rows[-1]["status"] == "rejected"
    assert state_repo.state == "idle"
    assert state_repo.saved == []
    assert execution_log.rows == []


def test_rejected_command_publishes_failure_event():
    device_id = uuid.uuid4()
    state_repo = FakeStateRepository("idle")
    command_log = FakeCommandLogRepository()
    execution_log = FakeExecutionLogRepository()
    event_bus = EventBus()
    observed = []
    event_bus.subscribe(CommandFailed, observed.append)
    service = CommandService(
        object(),
        devices=FakeDeviceRepository(SimpleNamespace(role="actuator", device_type="grow_light")),
        states=state_repo,
        executions=execution_log,
        command_log=command_log,
        event_bus=event_bus,
    )

    service.execute(device_id, "start_pump")

    assert len(observed) == 1
    assert observed[0].event_type == "command.failed"
    assert observed[0].device_id == device_id
