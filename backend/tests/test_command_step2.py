import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

from application.commands.service import CommandService


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
    )

    service.execute(device_id, "start_pump")

    assert command_log.rows[-1]["status"] == "rejected"
    assert state_repo.state == "running"


def test_start_pump_transitions_to_running():
    device_id = uuid.uuid4()
    state_repo = FakeStateRepository("idle")
    command_log = FakeCommandLogRepository()
    execution_log = FakeExecutionLogRepository()
    service = CommandService(
        object(),
        devices=FakeDeviceRepository(SimpleNamespace(role="actuator", device_type="water_pump")),
        states=state_repo,
        executions=execution_log,
        command_log=command_log,
    )

    service.execute(device_id, "start_pump", {"mode": "manual"})

    assert state_repo.state == "running"
    assert command_log.rows[-1]["status"] == "success"
    assert execution_log.rows[-1]["success"] is True


def test_set_light_level_succeeds_without_changing_running_state():
    device_id = uuid.uuid4()
    state_repo = FakeStateRepository("running")
    command_log = FakeCommandLogRepository()
    execution_log = FakeExecutionLogRepository()
    service = CommandService(
        object(),
        devices=FakeDeviceRepository(SimpleNamespace(role="actuator", device_type="grow_light")),
        states=state_repo,
        executions=execution_log,
        command_log=command_log,
    )

    service.execute(device_id, "set_light_level", {"level": 1})

    assert state_repo.state == "running"
    assert state_repo.saved == []
    assert command_log.rows[-1]["status"] == "success"
    assert execution_log.rows[-1]["success"] is True


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
    )

    service.execute(device_id, "start_pump")

    assert command_log.rows[-1]["status"] == "rejected"
    assert state_repo.state == "idle"
    assert state_repo.saved == []
    assert execution_log.rows == []
