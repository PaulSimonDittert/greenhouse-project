import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.alerts.subscribers import AlertPersistenceSubscriber
from application.readings.service import ReadingIngest
from domain.events.bus import EventBus
from domain.events.events import ReadingCreated

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL to an isolated PostgreSQL test database",
)


@pytest.fixture
def test_database():
    from infrastructure.persistence.models import Base

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        yield sessions
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def api_client(test_database):
    from infrastructure.db import get_db
    from main import app

    def override_get_db():
        with test_database() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        app.dependency_overrides.pop(get_db, None)


def test_read_inserts_sensor_reading(api_client: TestClient):
    created = api_client.post("/api/sensors", json={"type": "moisture"})
    assert created.status_code == 201, created.text
    device_id = created.json()["id"]

    first = api_client.post(f"/api/sensors/{device_id}/read")
    second = api_client.post(f"/api/sensors/{device_id}/read")
    history = api_client.get(f"/api/sensors/{device_id}/readings?limit=10")

    assert first.status_code == 201, first.text
    assert second.status_code == 201, second.text
    assert first.json()["device_id"] == device_id
    assert first.json()["unit"] == "vwc"
    assert first.json()["source"] == "simulation"
    assert len(history.json()) == 2
    assert all(reading["recorded_at"] for reading in history.json())


def test_sampler_respects_interval_and_tracking(test_database):
    from application.readings.sampler import SimulationSampler
    from infrastructure.persistence.models import DeviceRow, ReadingRow

    simulation_id = uuid.uuid4()
    disabled_id = uuid.uuid4()
    mqtt_id = uuid.uuid4()
    with test_database() as session:
        session.add_all(
            [
                DeviceRow(
                    id=simulation_id,
                    device_type="moisture_sensor",
                    role="sensor",
                    device_family="simulation",
                    display_name="Enabled simulation sensor",
                    default_config={"protocol": "simulation"},
                    sampling_interval_seconds=10,
                    tracking_enabled=True,
                ),
                DeviceRow(
                    id=disabled_id,
                    device_type="moisture_sensor",
                    role="sensor",
                    device_family="simulation",
                    display_name="Disabled simulation sensor",
                    default_config={"protocol": "simulation"},
                    sampling_interval_seconds=10,
                    tracking_enabled=False,
                ),
                DeviceRow(
                    id=mqtt_id,
                    device_type="moisture_sensor",
                    role="sensor",
                    device_family="edge",
                    display_name="MQTT sensor",
                    default_config={"protocol": "mqtt"},
                    sampling_interval_seconds=10,
                    tracking_enabled=True,
                ),
            ]
        )
        session.commit()

        start = datetime(2026, 9, 30, tzinfo=timezone.utc)
        sampler = SimulationSampler(session)
        sampler.run_once(start)
        assert session.query(ReadingRow).filter_by(device_id=simulation_id).count() == 1

        sampler.run_once(start + timedelta(seconds=9))
        assert session.query(ReadingRow).filter_by(device_id=simulation_id).count() == 1

        sampler.run_once(start + timedelta(seconds=10))
        assert session.query(ReadingRow).filter_by(device_id=simulation_id).count() == 2
        assert session.query(ReadingRow).filter_by(device_id=disabled_id).count() == 0
        assert session.query(ReadingRow).filter_by(device_id=mqtt_id).count() == 0


def test_reading_ingest_publishes_event_for_tracked_device(test_database):
    from domain.sensors.reading import Reading
    from infrastructure.persistence.models import DeviceRow, LocationRow, ZoneRow

    location_id = uuid.uuid4()
    zone_id = uuid.uuid4()
    sensor_id = uuid.uuid4()
    bus = EventBus()
    events = []
    bus.subscribe(ReadingCreated, events.append)

    with test_database() as session:
        session.add(LocationRow(id=location_id, name="North Wing"))
        session.add(
            ZoneRow(
                id=zone_id,
                location_id=location_id,
                name="Seed bed",
                moisture_threshold_low=0.25,
                moisture_threshold_high=0.5,
            )
        )
        session.commit()

        session.add(
            DeviceRow(
                id=sensor_id,
                device_type="moisture_sensor",
                role="sensor",
                device_family="simulation",
                display_name="Tracked sensor",
                default_config={"protocol": "simulation"},
                sampling_interval_seconds=300,
                tracking_enabled=True,
                zone_id=zone_id,
                location_id=location_id,
            )
        )
        session.commit()

        service = ReadingIngest(session, event_bus=bus)
        service.record(
            sensor_id,
            Reading(
                device_id=sensor_id,
                value=0.12,
                unit="vwc",
                source="manual",
                recorded_at=datetime(2026, 9, 30, 10, 0, tzinfo=timezone.utc),
            ),
        )

        assert len(events) == 1
        assert events[0].device_id == sensor_id
        assert events[0].zone_id == zone_id
        assert events[0].location_id == location_id
        assert events[0].event_type == "reading.created"


def test_reading_ingest_skips_publish_when_tracking_disabled(test_database):
    from domain.sensors.reading import Reading
    from infrastructure.persistence.models import DeviceRow, LocationRow, ZoneRow

    location_id = uuid.uuid4()
    zone_id = uuid.uuid4()
    sensor_id = uuid.uuid4()
    bus = EventBus()
    events = []
    bus.subscribe(ReadingCreated, events.append)

    with test_database() as session:
        session.add(LocationRow(id=location_id, name="South Wing"))
        session.add(
            ZoneRow(
                id=zone_id,
                location_id=location_id,
                name="Propagation",
                moisture_threshold_low=0.25,
                moisture_threshold_high=0.5,
            )
        )
        session.commit()

        session.add(
            DeviceRow(
                id=sensor_id,
                device_type="moisture_sensor",
                role="sensor",
                device_family="simulation",
                display_name="Untracked sensor",
                default_config={"protocol": "simulation"},
                sampling_interval_seconds=300,
                tracking_enabled=False,
                zone_id=zone_id,
                location_id=location_id,
            )
        )
        session.commit()

        service = ReadingIngest(session, event_bus=bus)
        service.record(
            sensor_id,
            Reading(
                device_id=sensor_id,
                value=0.10,
                unit="vwc",
                source="manual",
                recorded_at=datetime(2026, 9, 30, 10, 5, tzinfo=timezone.utc),
            ),
        )

        assert events == []


def test_alert_persistence_subscriber_inserts_threshold_alert(test_database):
    from infrastructure.persistence.models import AlertRow, DeviceRow, LocationRow, ZoneRow

    location_id = uuid.uuid4()
    zone_id = uuid.uuid4()
    sensor_id = uuid.uuid4()
    bus = EventBus()

    with test_database() as session:
        session.add(LocationRow(id=location_id, name="East Wing"))
        session.add(
            ZoneRow(
                id=zone_id,
                location_id=location_id,
                name="Moisture bed",
                moisture_threshold_low=0.35,
                moisture_threshold_high=0.6,
            )
        )
        session.commit()

        session.add(
            DeviceRow(
                id=sensor_id,
                device_type="moisture_sensor",
                role="sensor",
                device_family="simulation",
                display_name="Alerting sensor",
                default_config={"protocol": "simulation"},
                sampling_interval_seconds=300,
                tracking_enabled=True,
                zone_id=zone_id,
                location_id=location_id,
            )
        )
        session.commit()

        AlertPersistenceSubscriber(session).subscribe(bus)
        bus.publish(
            ReadingCreated(
                device_id=sensor_id,
                value=0.12,
                unit="vwc",
                source="manual",
                recorded_at=datetime(2026, 9, 30, 10, 15, tzinfo=timezone.utc),
                location_id=location_id,
                zone_id=zone_id,
            )
        )

        stored = session.query(AlertRow).filter_by(device_id=sensor_id).one()
        assert stored.event_type == "threshold.crossed"
        assert stored.severity == "warning"
        assert stored.status == "active"
        assert stored.location_id == location_id
        assert stored.zone_id == zone_id
        assert "below the low threshold" in stored.message


def test_alerts_api_filters_by_status_and_zone(test_database):
    from infrastructure.db import get_db
    from infrastructure.persistence.models import AlertRow, DeviceRow, LocationRow, ZoneRow
    from main import app

    location_id = uuid.uuid4()
    zone_id = uuid.uuid4()
    other_zone = uuid.uuid4()
    device_id = uuid.uuid4()
    other_device_id = uuid.uuid4()

    with test_database() as session:
        session.add(LocationRow(id=location_id, name="Filtered location"))
        session.add_all(
            [
                ZoneRow(
                    id=zone_id,
                    location_id=location_id,
                    name="Filtered zone",
                    moisture_threshold_low=0.2,
                    moisture_threshold_high=0.5,
                ),
                ZoneRow(
                    id=other_zone,
                    location_id=location_id,
                    name="Other zone",
                    moisture_threshold_low=0.2,
                    moisture_threshold_high=0.5,
                ),
            ]
        )
        session.commit()

        session.add_all(
            [
                DeviceRow(
                    id=device_id,
                    device_type="moisture_sensor",
                    role="sensor",
                    device_family="simulation",
                    display_name="Primary sensor",
                    default_config={"protocol": "simulation"},
                    sampling_interval_seconds=300,
                    tracking_enabled=True,
                    zone_id=zone_id,
                    location_id=location_id,
                ),
                DeviceRow(
                    id=other_device_id,
                    device_type="moisture_sensor",
                    role="sensor",
                    device_family="simulation",
                    display_name="Secondary sensor",
                    default_config={"protocol": "simulation"},
                    sampling_interval_seconds=300,
                    tracking_enabled=True,
                    zone_id=other_zone,
                    location_id=location_id,
                ),
            ]
        )
        session.commit()

        session.add(
            AlertRow(
                location_id=location_id,
                zone_id=zone_id,
                device_id=device_id,
                severity="warning",
                message="Threshold crossed in zone one",
                event_type="threshold.crossed",
                status="active",
            )
        )
        session.add(
            AlertRow(
                location_id=location_id,
                zone_id=other_zone,
                device_id=other_device_id,
                severity="critical",
                message="Another alert",
                event_type="command.failed",
                status="active",
            )
        )
        session.commit()

    def override_get_db():
        with test_database() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        response = client.get(
            "/api/alerts",
            params={"status": "active", "location_id": str(location_id), "zone_id": str(zone_id)},
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["zone_id"] == str(zone_id)
        assert payload[0]["event_type"] == "threshold.crossed"
    finally:
        client.close()
        app.dependency_overrides.pop(get_db, None)