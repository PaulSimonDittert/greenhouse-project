import pytest

from domain.actuators.context import ActuatorContext
from domain.actuators.state import IllegalTransitionError


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
