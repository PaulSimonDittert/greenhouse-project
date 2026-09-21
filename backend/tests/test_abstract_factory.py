from domain.devices.family_factory import SimulationDeviceFactory, EdgeHardwareFactory

def test_simulation_factory_returns_four_devices():
    factory = SimulationDeviceFactory()
    devices = factory.create_device_set()
    
    # Check that exactly 4 devices are provisioned
    assert len(devices) == 4
    
    # Check that all belong to the simulation family
    assert all(d.device_family == "simulation" for d in devices)
    
    # Check that both sensors and actuators are included in the kit
    roles = {d.role for d in devices}
    assert "sensor" in roles
    assert "actuator" in roles

def test_edge_factory_differs_from_simulation():
    sim_factory = SimulationDeviceFactory()
    edge_factory = EdgeHardwareFactory()
    
    sim_devices = sim_factory.create_device_set()
    edge_devices = edge_factory.create_device_set()
    
    # Ensure they have different family keys
    assert sim_factory.family_key == "simulation"
    assert edge_factory.family_key == "edge"
    
    # Ensure their configurations (e.g., protocols) actually differ
    sim_pump = next(d for d in sim_devices if d.device_type == "water_pump")
    edge_pump = next(d for d in edge_devices if d.device_type == "water_pump")
    
    assert sim_pump.default_config["protocol"] == "sim-virtual"
    assert edge_pump.default_config["protocol"] == "gpio-relay"