import pytest

from domain.locations.config_builder import LocationConfigBuilder
from domain.locations.errors import ConfigurationError


def test_build_success():
    config = (
        LocationConfigBuilder()
        .with_location_name("Greenhouse A")
        .add_zone("North bed", 0.25, 0.65, {"days": ["Mon", "Thu"]})
        .build()
    )

    assert config.location.name == "Greenhouse A"
    assert len(config.zones) == 1
    assert config.zones[0].name == "North bed"
    assert config.zones[0].moisture_threshold_low == 0.25
    assert config.zones[0].moisture_threshold_high == 0.65
    assert config.zones[0].schedule == {"days": ["Mon", "Thu"]}


def test_build_requires_name():
    builder = LocationConfigBuilder().add_zone("North bed", 0.25, 0.65)

    with pytest.raises(ConfigurationError, match="Location name is required"):
        builder.build()


def test_build_requires_zones():
    builder = LocationConfigBuilder().with_location_name("Greenhouse A")

    with pytest.raises(ConfigurationError, match="At least one zone is required"):
        builder.build()


def test_build_rejects_invalid_thresholds():
    builder = LocationConfigBuilder().with_location_name("Greenhouse A")

    with pytest.raises(ConfigurationError, match="strictly less"):
        builder.add_zone("North bed", 0.7, 0.6)