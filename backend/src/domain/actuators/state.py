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
    "idle": ["start_pump", "set_light_level"],
    "running": ["stop_pump", "set_light_level"],
    "error": ["reset"],
    "maintenance": ["resume_operation"],
}

COMMANDS_BY_DEVICE_TYPE: dict[str, set[str]] = {
    "water_pump": {"start_pump", "stop_pump"},
    "grow_light": {"set_light_level"},
}


class IllegalTransitionError(ValueError):
    """Raised when an actuator transition is not allowed for the current state."""


def get_allowed_commands(state: str, device_type: str | None = None) -> list[str]:
    if state not in VALID_STATES:
        raise ValueError(f"Unknown actuator state: {state}")
    commands = ALLOWED_COMMANDS[state]
    if device_type is None:
        return list(commands)
    device_commands = COMMANDS_BY_DEVICE_TYPE.get(device_type, set())
    return [command for command in commands if command in device_commands]


def can_transition(current_state: str, target_state: str) -> bool:
    if current_state not in VALID_STATES:
        raise ValueError(f"Unknown actuator state: {current_state}")
    if target_state not in VALID_STATES:
        raise ValueError(f"Unknown actuator state: {target_state}")
    return target_state in ALLOWED_TRANSITIONS.get(current_state, set())
