import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    from domain.devices.entity import Device
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