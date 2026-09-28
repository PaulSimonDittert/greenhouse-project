import uuid
from sqlalchemy.orm import Session
from infrastructure.persistence.models import DeviceRow, ZoneRow

class ZoneAssignmentService:
    def __init__(self, db: Session):
        self.db = db
        
    def assign(self, device_id: uuid.UUID, zone_id: uuid.UUID | None) -> None:
        device = self.db.query(DeviceRow).filter(DeviceRow.id == device_id).first()
        if not device:
            raise ValueError("Device not found")
            
        if zone_id is not None:
            zone = self.db.query(ZoneRow).filter(ZoneRow.id == zone_id).first()
            if not zone:
                raise ValueError("Zone not found")
            
            device.zone_id = zone.id
            device.location_id = zone.location_id
        else:
            device.zone_id = None
            device.location_id = None
            
        self.db.commit()
        
    def list_devices(self, location_id: uuid.UUID, zone_id: uuid.UUID) -> list[DeviceRow]:
        zone = self.db.query(ZoneRow).filter(ZoneRow.id == zone_id, ZoneRow.location_id == location_id).first()
        if not zone:
            raise ValueError("Zone not found in location")
        return self.db.query(DeviceRow).filter(DeviceRow.zone_id == zone_id).all()