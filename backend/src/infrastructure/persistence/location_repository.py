import uuid
from sqlalchemy.orm import Session
from domain.locations.entity import LocationConfig
from infrastructure.persistence.models import LocationRow, ZoneRow, DeviceRow

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_config(self, config: LocationConfig) -> tuple[LocationRow, list[ZoneRow]]:
        # 1. Save the location
        loc_row = LocationRow(name=config.location.name)
        self.db.add(loc_row)
        self.db.flush()

        zone_rows = []
        for z in config.zones:
            z_row = ZoneRow(
                location_id=loc_row.id,
                name=z.name,
                moisture_threshold_low=z.moisture_threshold_low,
                moisture_threshold_high=z.moisture_threshold_high,
                schedule=z.schedule
            )
            self.db.add(z_row)
            zone_rows.append(z_row)
        
        self.db.commit()
        
        self.db.refresh(loc_row)
        for z_row in zone_rows:
            self.db.refresh(z_row)
            
        return loc_row, zone_rows

    def get_config(self, location_id: uuid.UUID) -> tuple[LocationRow, list[ZoneRow]] | None:
        loc_row = self.db.query(LocationRow).filter(LocationRow.id == location_id).first()
        if not loc_row:
            return None
        zone_rows = self.db.query(ZoneRow).filter(ZoneRow.location_id == location_id).all()
        return loc_row, zone_rows