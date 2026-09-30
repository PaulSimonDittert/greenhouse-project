import uuid

from domain.actuators.ports import ActuatorPort
from infrastructure.adapters.actuators.simulation import SimulationActuatorAdapter


def test_simulation_actuator_records_apply_intent():
    adapter = SimulationActuatorAdapter()
    device_id = uuid.uuid4()
    payload = {"duration_seconds": 5}

    adapter.apply(device_id, "activate", payload)
    payload["duration_seconds"] = 10

    assert isinstance(adapter, ActuatorPort)
    assert len(adapter.applied_commands) == 1
    assert adapter.applied_commands[0].device_id == device_id
    assert adapter.applied_commands[0].command == "activate"
    assert adapter.applied_commands[0].payload == {"duration_seconds": 5}