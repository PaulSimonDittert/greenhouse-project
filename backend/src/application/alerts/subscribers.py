from __future__ import annotations

from sqlalchemy.orm import Session

from domain.events.events import CommandFailed, ReadingCreated, ThresholdCrossed
from infrastructure.persistence.alert_repository import AlertRepository
from infrastructure.persistence.models import DeviceRow, ZoneRow


class AlertPersistenceSubscriber:
    def __init__(self, db: Session, repository: AlertRepository | None = None):
        self.db = db
        self.repository = repository or AlertRepository(db)

    def subscribe(self, event_bus) -> "AlertPersistenceSubscriber":
        event_bus.subscribe(ReadingCreated, self.on_reading_created)
        event_bus.subscribe(ThresholdCrossed, self.on_threshold_crossed)
        event_bus.subscribe(CommandFailed, self.on_command_failed)
        return self

    def on_reading_created(self, event: ReadingCreated) -> None:
        device = self.db.query(DeviceRow).filter(DeviceRow.id == event.device_id).first() if event.device_id else None
        zone_id = event.zone_id if event.zone_id is not None else (device.zone_id if device else None)
        location_id = event.location_id if event.location_id is not None else (device.location_id if device else None)
        if zone_id is None:
            return

        zone = self.db.query(ZoneRow).filter(ZoneRow.id == zone_id).first()
        if zone is None or event.value >= zone.moisture_threshold_low:
            return

        self.repository.insert(
            location_id=location_id,
            zone_id=zone_id,
            device_id=event.device_id,
            severity="warning",
            message=(
                f"Moisture {event.value:.2f} is below the low threshold "
                f"{zone.moisture_threshold_low:.2f}"
            ),
            event_type="threshold.crossed",
            status="active",
        )

    def on_threshold_crossed(self, event: ThresholdCrossed) -> None:
        self.repository.insert(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity=event.severity,
            message=event.message or f"Threshold crossed at {event.value:.2f}",
            event_type=event.event_type,
            status="active",
        )

    def on_command_failed(self, event: CommandFailed) -> None:
        self.repository.insert(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="critical",
            message=event.error_message or "Command failure",
            event_type=event.event_type,
            status="active",
        )
