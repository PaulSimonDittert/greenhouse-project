from abc import ABC, abstractmethod
from domain.devices.entity import Device
from domain.sensors.creators import get_creator

class DeviceFamilyFactory(ABC):
    @property
    @abstractmethod
    def family_key(self) -> str:
        pass

    @abstractmethod
    def create_device_set(self) -> list[Device]:
        pass

class SimulationDeviceFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "simulation"

    def create_device_set(self) -> list[Device]:
        moisture_creator = get_creator("moisture")
        light_creator = get_creator("light")
        
        m_sensor = moisture_creator.create_sensor(display_name="Sim Moisture Sensor")
        l_sensor = light_creator.create_sensor(display_name="Sim Light Sensor")
        
        d1 = Device(id=None, device_type=m_sensor.device_type, role="sensor", device_family=self.family_key, display_name=m_sensor.display_name, default_config={"protocol": "sim-virtual", **m_sensor.default_config})
        d2 = Device(id=None, device_type=l_sensor.device_type, role="sensor", device_family=self.family_key, display_name=l_sensor.display_name, default_config={"protocol": "sim-virtual", **l_sensor.default_config})
        
        d3 = Device(id=None, device_type="water_pump", role="actuator", device_family=self.family_key, display_name="Sim Water Pump", default_config={"protocol": "sim-virtual", "flow_rate": 1.5})
        d4 = Device(id=None, device_type="grow_light", role="actuator", device_family=self.family_key, display_name="Sim Grow Light", default_config={"protocol": "sim-virtual", "lumens": 5000})
        
        return [d1, d2, d3, d4]

class EdgeHardwareFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "edge"

    def create_device_set(self) -> list[Device]:
        moisture_creator = get_creator("moisture")
        light_creator = get_creator("light")
        
        m_sensor = moisture_creator.create_sensor(display_name="Edge Moisture Sensor")
        l_sensor = light_creator.create_sensor(display_name="Edge Light Sensor")
        
        d1 = Device(id=None, device_type=m_sensor.device_type, role="sensor", device_family=self.family_key, display_name=m_sensor.display_name, default_config={"protocol": "gpio-i2c", **m_sensor.default_config})
        d2 = Device(id=None, device_type=l_sensor.device_type, role="sensor", device_family=self.family_key, display_name=l_sensor.display_name, default_config={"protocol": "gpio-spi", **l_sensor.default_config})
        
        d3 = Device(id=None, device_type="water_pump", role="actuator", device_family=self.family_key, display_name="Edge Water Pump", default_config={"protocol": "gpio-relay", "relay_pin": 17})
        d4 = Device(id=None, device_type="grow_light", role="actuator", device_family=self.family_key, display_name="Edge Grow Light", default_config={"protocol": "gpio-relay", "relay_pin": 18})
        
        return [d1, d2, d3, d4]

def get_family_factory(family: str) -> DeviceFamilyFactory:
    if family == "simulation":
        return SimulationDeviceFactory()
    elif family == "edge":
        return EdgeHardwareFactory()
    else:
        raise ValueError(f"Unknown device family: {family}")