import uuid
from sqlalchemy.orm import Session
from domain.locations.config_builder import LocationConfigBuilder
from domain.locations.errors import ConfigurationError
from application.locations.dto import BuildLocationConfigRequestDto
from infrastructure.persistence.location_repository import LocationRepository
from infrastructure.persistence.models import LocationRow, ZoneRow, DeviceRow

class LocationConfigService:
    def __init__(self, db: Session):
        self.db = db
        self._repo = LocationRepository(db)

    def build_and_save(self, request: BuildLocationConfigRequestDto) -> tuple[LocationRow, list[ZoneRow]]:
        builder = LocationConfigBuilder().with_location_name(request.location_name)
        for z in request.zones:
            builder.add_zone(
                name=z.name,
                moisture_threshold_low=z.moisture_threshold_low,
                moisture_threshold_high=z.moisture_threshold_high,
                schedule=z.schedule
            )
        config = builder.build()
        return self._repo.save_config(config)
        
    def list_locations(self) -> list[LocationRow]:
        return self.db.query(LocationRow).order_by(LocationRow.created_at.asc()).all()
        
    def delete_location(self, location_id: uuid.UUID) -> bool:
        loc_row = self.db.query(LocationRow).filter(LocationRow.id == location_id).first()
        if not loc_row:
            return False
        self.db.delete(loc_row)
        self.db.commit()
        return True

    def _validate_zone_fields(self, name: str, low: float, high: float) -> str:
        clean = name.strip() if name else ""
        if not clean:
            raise ConfigurationError("Zone name cannot be empty")
        if low < 0.0 or high > 1.0:
            raise ConfigurationError("Thresholds must be between 0.0 and 1.0 (VWC)")
        if low >= high:
            raise ConfigurationError("Low threshold must be strictly less than high threshold")
        return clean

    def add_zone(self, location_id: uuid.UUID, name: str, low: float, high: float, schedule: dict | None) -> ZoneRow:
        clean_name = self._validate_zone_fields(name, low, high)
        z = ZoneRow(location_id=location_id, name=clean_name, moisture_threshold_low=low, moisture_threshold_high=high, schedule=schedule)
        self.db.add(z)
        self.db.commit()
        self.db.refresh(z)
        return z

    def update_zone(self, location_id: uuid.UUID, zone_id: uuid.UUID, name: str, low: float, high: float, schedule: dict | None) -> ZoneRow:
        clean_name = self._validate_zone_fields(name, low, high)
        z = self.db.query(ZoneRow).filter(ZoneRow.id == zone_id, ZoneRow.location_id == location_id).first()
        if not z:
            raise ValueError("Zone not found")
        
        z.name = clean_name
        z.moisture_threshold_low = low
        z.moisture_threshold_high = high
        z.schedule = schedule
        self.db.commit()
        self.db.refresh(z)
        return z

    def delete_zone(self, location_id: uuid.UUID, zone_id: uuid.UUID) -> None:
        zone_count = self.db.query(ZoneRow).filter(ZoneRow.location_id == location_id).count()
        if zone_count <= 1:
            raise ConfigurationError("Cannot delete the last remaining zone in a location")
            
        z = self.db.query(ZoneRow).filter(ZoneRow.id == zone_id, ZoneRow.location_id == location_id).first()
        if not z:
            raise ValueError("Zone not found")
            
        self.db.query(DeviceRow).filter(DeviceRow.zone_id == zone_id).update(
            {"zone_id": None, "location_id": None}, synchronize_session=False
        )
        self.db.delete(z)
        self.db.commit()