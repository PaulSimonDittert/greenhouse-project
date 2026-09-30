import uuid
from datetime import timezone

from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from infrastructure.adapters.sensors.simulation import SimulationSensorAdapter
from infrastructure.adapters.sensors.vendor_stub import VendorStubSensorAdapter


def make_moisture_device() -> Device:
    return Device(
        id=uuid.uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Test moisture sensor",
        default_config={},
    )


def test_vendor_adapter_normalizes_raw_payload():
    device = make_moisture_device()

    reading = VendorStubSensorAdapter().translate(
        device,
        {"measurement": {"reading": 41, "scale": "percent"}},
    )

    assert reading.device_id == device.id
    assert reading.value == 0.41
    assert reading.unit == "vwc"
    assert reading.source == "vendor"
    assert reading.recorded_at.tzinfo == timezone.utc


def test_simulation_adapter_value_in_range():
    adapter = SimulationSensorAdapter()
    moisture_device = make_moisture_device()
    light_device = Device(
        id=uuid.uuid4(),
        device_type="light_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Test light sensor",
        default_config={},
    )

    moisture = adapter.read(moisture_device)
    light = adapter.read(light_device)

    assert isinstance(adapter, SensorPort)
    assert 0.2 <= moisture.value <= 0.6
    assert moisture.unit == "vwc"
    assert moisture.source == "simulation"
    assert 200 <= light.value <= 2000
    assert light.unit == "lux"
    assert light.source == "simulation"


def test_mqtt_adapter_translates_payload():
    device = make_moisture_device()

    reading = MqttSensorAdapter().translate(device, {"value": 0.41, "unit": "vwc"})

    assert reading.device_id == device.id
    assert reading.value == 0.41
    assert reading.unit == "vwc"
    assert reading.source == "mqtt"
    assert reading.recorded_at.tzinfo == timezone.utc