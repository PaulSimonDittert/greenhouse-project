VALID_STATES = {"off", "idle", "running", "error", "maintenance"}

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "off": {"idle"},
    "idle": {"running", "maintenance", "error"},
    "running": {"idle", "error"},
    "error": {"idle", "off"},
    "maintenance": {"idle", "error"},
}

ALLOWED_COMMANDS: dict[str, list[str]] = {
    "off": ["start_pump"],
    "idle": ["start_pump"],
    "running": ["stop_pump"],
    "error": ["reset"],
    "maintenance": ["resume_operation"],
}


class IllegalTransitionError(ValueError):
    """Raised when an actuator transition is not allowed for the current state."""


def get_allowed_commands(state: str) -> list[str]:
    if state not in VALID_STATES:
        raise ValueError(f"Unknown actuator state: {state}")
    return list(ALLOWED_COMMANDS[state])


def can_transition(current_state: str, target_state: str) -> bool:
    if current_state not in VALID_STATES:
        raise ValueError(f"Unknown actuator state: {current_state}")
    if target_state not in VALID_STATES:
        raise ValueError(f"Unknown actuator state: {target_state}")
    return target_state in ALLOWED_TRANSITIONS.get(current_state, set())
