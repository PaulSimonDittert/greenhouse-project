from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from infrastructure.adapters.sensors.simulation import SimulationSensorAdapter
from infrastructure.adapters.sensors.vendor_stub import VendorStubSensorAdapter


def select_sensor_adapter(device: Device) -> SensorPort | MqttSensorAdapter:
    """Select by protocol; sensor_adapter='vendor_stub' explicitly opts into the vendor exercise."""
    if device.default_config.get("sensor_adapter") == "vendor_stub":
        return VendorStubSensorAdapter()

    protocol = device.default_config.get("protocol", "simulation")
    if protocol in {"simulation", "sim-virtual"}:
        return SimulationSensorAdapter()
    if protocol == "mqtt":
        return MqttSensorAdapter()
    raise ValueError(f"Unsupported sensor protocol: {protocol}")