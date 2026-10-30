from domain.actuators.context import ActuatorContext
from domain.devices.entity import Device
from application.devices.dto import DeviceDto


def device_to_dto(device: Device, state: str | None = None, allowed_commands: list[str] | None = None) -> DeviceDto:
    if device.id is None:
        raise ValueError("Cannot map unpersisted device to DTO")

    actuator_state = state if state is not None else "idle"
    commands = allowed_commands if allowed_commands is not None else ActuatorContext(actuator_state).allowed_commands

    return DeviceDto(
        id=device.id,
        device_type=device.device_type,
        role=device.role,
        device_family=device.device_family,
        display_name=device.display_name,
        default_config=device.default_config,
        zone_id=device.zone_id,
        location_id=device.location_id,
        state=actuator_state,
        allowed_commands=commands,
    )


def devices_to_dtos(devices: list[Device], states: dict[object, str] | None = None) -> list[DeviceDto]:
    state_lookup = states or {}
    return [
        device_to_dto(
            d,
            state=state_lookup.get(d.id),
            allowed_commands=ActuatorContext(state_lookup.get(d.id) or "idle").allowed_commands if d.role == "actuator" else [],
        )
        for d in devices
    ]