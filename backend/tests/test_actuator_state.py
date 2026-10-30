import uuid

import pytest

from application.devices.actuator_state_service import ActuatorStateService
from domain.actuators.context import ActuatorContext
from domain.actuators.state import IllegalTransitionError
from domain.devices.entity import Device


@pytest.mark.parametrize(
    ("start", "target"),
    [
        ("idle", "running"),
        ("running", "idle"),
        ("idle", "error"),
        ("error", "idle"),
        ("off", "idle"),
        ("maintenance", "idle"),
    ],
)
def test_allowed_transitions(start: str, target: str) -> None:
    context = ActuatorContext(start)

    assert context.transition(target) == target
    assert context.state == target


@pytest.mark.parametrize(
    ("start", "target"),
    [
        ("idle", "off"),
        ("running", "maintenance"),
        ("maintenance", "running"),
        ("off", "running"),
        ("error", "running"),
    ],
)
def test_illegal_transitions_are_rejected(start: str, target: str) -> None:
    context = ActuatorContext(start)

    with pytest.raises(IllegalTransitionError):
        context.transition(target)

    assert context.state == start


def test_allowed_commands_follow_current_state() -> None:
    assert ActuatorContext("idle").allowed_commands == ["start_pump"]
    assert ActuatorContext("running").allowed_commands == ["stop_pump"]
    assert ActuatorContext("error").allowed_commands == ["reset"]


class FakeDeviceRepository:
    def __init__(self, devices: dict[uuid.UUID, Device]):
        self.devices = devices

    def get_device(self, device_id: uuid.UUID) -> Device | None:
        return self.devices.get(device_id)


class FakeStateRepository:
    def __init__(self, initial: dict[uuid.UUID, str]):
        self.store = dict(initial)
        self.saved: list[tuple[uuid.UUID, str]] = []

    def get_for_device(self, device_id: uuid.UUID) -> str | None:
        return self.store.get(device_id)

    def save(self, device_id: uuid.UUID, state: str) -> str:
        self.saved.append((device_id, state))
        self.store[device_id] = state
        return state


def test_service_persists_valid_transition_only() -> None:
    device_id = uuid.uuid4()
    device = Device(
        id=device_id,
        device_type="water_pump",
        role="actuator",
        device_family="simulation",
        display_name="Pump",
        default_config={"protocol": "sim-virtual"},
    )
    service = ActuatorStateService.__new__(ActuatorStateService)
    service._devices = FakeDeviceRepository({device_id: device})
    service._states = FakeStateRepository({device_id: "idle"})

    result = service.transition(device_id, "running")

    assert result == "running"
    assert service._states.store[device_id] == "running"
    assert service._states.saved == [(device_id, "running")]


def test_service_does_not_persist_illegal_transition() -> None:
    device_id = uuid.uuid4()
    device = Device(
        id=device_id,
        device_type="water_pump",
        role="actuator",
        device_family="simulation",
        display_name="Pump",
        default_config={"protocol": "sim-virtual"},
    )
    service = ActuatorStateService.__new__(ActuatorStateService)
    service._devices = FakeDeviceRepository({device_id: device})
    service._states = FakeStateRepository({device_id: "idle"})

    with pytest.raises(IllegalTransitionError):
        service.transition(device_id, "off")

    assert service._states.store[device_id] == "idle"
    assert service._states.saved == []
