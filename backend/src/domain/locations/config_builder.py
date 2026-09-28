from .entity import Location, Zone, LocationConfig
from .errors import ConfigurationError

class LocationConfigBuilder:
    def __init__(self):
        self._location_name: str | None = None
        self._zones: list[Zone] = []

    def with_location_name(self, name: str) -> "LocationConfigBuilder":
        if not name or not name.strip():
            raise ConfigurationError("Location name cannot be empty")
        self._location_name = name.strip()
        return self

    def add_zone(
        self,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict | None = None,
    ) -> "LocationConfigBuilder":
        clean_name = name.strip() if name else ""
        if not clean_name:
            raise ConfigurationError("Zone name cannot be empty")
            
        if moisture_threshold_low < 0.0 or moisture_threshold_high > 1.0:
            raise ConfigurationError("Thresholds must be between 0.0 and 1.0 (VWC)")
            
        if moisture_threshold_low >= moisture_threshold_high:
            raise ConfigurationError("Low threshold must be strictly less than high threshold")

        if any(z.name == clean_name for z in self._zones):
            raise ConfigurationError(f"Zone name '{clean_name}' must be unique within the location")

        self._zones.append(Zone(
            name=clean_name,
            moisture_threshold_low=moisture_threshold_low,
            moisture_threshold_high=moisture_threshold_high,
            schedule=schedule
        ))
        return self

    def build(self) -> LocationConfig:
        if not self._location_name:
            raise ConfigurationError("Location name is required")
        if not self._zones:
            raise ConfigurationError("At least one zone is required")

        return LocationConfig(
            location=Location(name=self._location_name),
            zones=tuple(self._zones)
        )