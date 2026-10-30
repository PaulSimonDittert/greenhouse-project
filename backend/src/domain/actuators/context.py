from dataclasses import dataclass

from domain.actuators.state import (
    IllegalTransitionError,
    VALID_STATES,
    can_transition,
    get_allowed_commands,
)


@dataclass
class ActuatorContext:
    state: str = "idle"

    def __post_init__(self) -> None:
        if self.state not in VALID_STATES:
            raise ValueError(f"Unknown actuator state: {self.state}")

    @property
    def allowed_commands(self) -> list[str]:
        return get_allowed_commands(self.state)

    def transition(self, target: str) -> str:
        if not can_transition(self.state, target):
            raise IllegalTransitionError(
                f"Illegal actuator transition from '{self.state}' to '{target}'."
            )
        self.state = target
        return self.state
