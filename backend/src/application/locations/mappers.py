from application.locations.dto import LocationDto, ZoneDto, LocationConfigDto
from infrastructure.persistence.models import LocationRow, ZoneRow

def location_row_to_dto(row: LocationRow) -> LocationDto:
    return LocationDto(id=row.id, name=row.name)

def zone_row_to_dto(row: ZoneRow) -> ZoneDto:
    return ZoneDto(
        id=row.id,
        location_id=row.location_id,
        name=row.name,
        moisture_threshold_low=row.moisture_threshold_low,
        moisture_threshold_high=row.moisture_threshold_high,
        schedule=row.schedule
    )

def location_config_to_dto(loc_row: LocationRow, zone_rows: list[ZoneRow]) -> LocationConfigDto:
    return LocationConfigDto(
        location=location_row_to_dto(loc_row),
        zones=[zone_row_to_dto(z) for z in zone_rows]
    )