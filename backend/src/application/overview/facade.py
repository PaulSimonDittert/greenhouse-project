import uuid

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from application.automation.service import AutomationService
from application.overview.dto import (
    DeviceCountsDto,
    LatestReadingDto,
    LocationOverviewDto,
    LocationSummaryDto,
    OverviewDeviceDto,
    OverviewZoneDto,
    RecommendationDto,
)
from infrastructure.persistence.automation_repository import AutomationRuleRepository
from infrastructure.persistence.location_repository import LocationRepository
from infrastructure.persistence.models import DeviceRow, ReadingRow


class LocationOverviewFacade:
    def __init__(self, db: Session):
        self.db = db
        self._location_repo = LocationRepository(db)
        self._automation_repo = AutomationRuleRepository(db)
        self._automation_service = AutomationService(db)

    def get_overview(self, location_id: uuid.UUID) -> LocationOverviewDto:
        config = self._location_repo.get_config(location_id)
        if config is None:
            raise ValueError("Location not found")

        location_row, zone_rows = config

        assigned_devices = (
            self.db.query(DeviceRow)
            .filter(DeviceRow.location_id == location_id, DeviceRow.zone_id.is_not(None))
            .order_by(DeviceRow.created_at.desc(), DeviceRow.id)
            .all()
        )

        device_counts = DeviceCountsDto(sensor=0, actuator=0)
        for device in assigned_devices:
            if device.role == "sensor":
                device_counts.sensor += 1
            elif device.role == "actuator":
                device_counts.actuator += 1

        latest_readings_by_device = self._latest_readings_for_devices(assigned_devices)

        overview_zones: list[OverviewZoneDto] = []
        for zone in zone_rows:
            zone_devices = [
                OverviewDeviceDto(
                    id=device.id,
                    device_type=device.device_type,
                    role=device.role,
                    display_name=device.display_name or device.device_type,
                )
                for device in assigned_devices
                if device.zone_id == zone.id
            ]
            latest_readings = [
                self._make_latest_reading_dto(latest_readings_by_device[device.id])
                for device in assigned_devices
                if device.zone_id == zone.id and device.id in latest_readings_by_device
            ]
            latest_readings.sort(key=lambda reading: reading.recorded_at, reverse=True)

            overview_zones.append(
                OverviewZoneDto(
                    id=zone.id,
                    name=zone.name,
                    moisture_threshold_low=zone.moisture_threshold_low,
                    moisture_threshold_high=zone.moisture_threshold_high,
                    devices=zone_devices,
                    latest_readings=latest_readings,
                )
            )

        strategy_row = self._automation_repo.get_for_location(location_id)
        strategy_key = strategy_row.strategy_key if strategy_row else None

        last_recommendation = None
        if strategy_key is not None:
            recommendation = self._automation_service.evaluate(location_id)
            last_recommendation = RecommendationDto(
                action=recommendation.action,
                reason=recommendation.reason,
            )

        return LocationOverviewDto(
            location=LocationSummaryDto(id=location_row.id, name=location_row.name),
            device_counts=device_counts,
            zones=overview_zones,
            strategy_key=strategy_key,
            last_recommendation=last_recommendation,
        )

    def _latest_readings_for_devices(self, assigned_devices: list[DeviceRow]) -> dict[uuid.UUID, tuple[ReadingRow, bool, int]]:
        if not assigned_devices:
            return {}

        device_ids = [device.id for device in assigned_devices]
        latest_timestamp_subquery = (
            self.db.query(
                ReadingRow.device_id.label("device_id"),
                func.max(ReadingRow.recorded_at).label("recorded_at"),
            )
            .filter(ReadingRow.device_id.in_(device_ids))
            .group_by(ReadingRow.device_id)
            .subquery()
        )

        rows = (
            self.db.query(ReadingRow, DeviceRow.tracking_enabled, DeviceRow.sampling_interval_seconds)
            .join(
                latest_timestamp_subquery,
                and_(
                    ReadingRow.device_id == latest_timestamp_subquery.c.device_id,
                    ReadingRow.recorded_at == latest_timestamp_subquery.c.recorded_at,
                ),
            )
            .join(DeviceRow, DeviceRow.id == ReadingRow.device_id)
            .filter(ReadingRow.device_id.in_(device_ids))
            .all()
        )

        latest_by_device: dict[uuid.UUID, tuple[ReadingRow, bool, int]] = {}
        for reading_row, tracking_enabled, sampling_interval_seconds in rows:
            latest_by_device[reading_row.device_id] = (
                reading_row,
                bool(tracking_enabled),
                int(sampling_interval_seconds),
            )
        return latest_by_device

    def _make_latest_reading_dto(self, reading_data: tuple[ReadingRow, bool, int]) -> LatestReadingDto:
        reading_row, tracking_enabled, sampling_interval_seconds = reading_data
        return LatestReadingDto(
            device_id=reading_row.device_id,
            value=float(reading_row.value),
            unit=reading_row.unit,
            recorded_at=reading_row.recorded_at,
            tracking_enabled=tracking_enabled,
            sampling_interval_seconds=sampling_interval_seconds,
        )
