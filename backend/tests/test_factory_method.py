import pytest
from domain.sensors.creators import MoistureSensorCreator, LightSensorCreator, get_creator

def test_moisture_creator_defaults():
    creator = MoistureSensorCreator()
    sensor = creator.create_sensor()
    
    assert sensor.device_type == "moisture_sensor"
    assert "threshold" in sensor.default_config
    assert sensor.default_config["unit"] == "vwc"

def test_light_creator_defaults():
    creator = LightSensorCreator()
    sensor = creator.create_sensor()
    
    assert sensor.device_type == "light_sensor"
    assert sensor.default_config["unit"] == "lux"
    assert sensor.default_config["unit"] != MoistureSensorCreator().create_sensor().default_config["unit"]

def test_get_creator_registry():
    moisture_creator = get_creator("moisture")
    light_creator = get_creator("light")
    
    assert isinstance(moisture_creator, MoistureSensorCreator)
    assert isinstance(light_creator, LightSensorCreator)

def test_get_creator_unknown_type():
    with pytest.raises(ValueError) as exc_info:
        get_creator("unknown_sensor")
    assert "Unknown sensor type" in str(exc_info.value)