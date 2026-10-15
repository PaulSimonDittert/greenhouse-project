import os
import uuid
from datetime import datetime, timezone

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
    test_sessions = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        yield test_sessions
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


def test_overview_returns_strategy_and_readings(api_client: TestClient, test_database):
    from infrastructure.persistence.models import (
        DeviceRow,
        LocationRow,
        ReadingRow,
        ZoneRow,
    )

    location_id = uuid.uuid4()
    first_zone_id = uuid.uuid4()
    empty_zone_id = uuid.uuid4()
    assigned_device_id = uuid.uuid4()
    unassigned_device_id = uuid.uuid4()
    recorded_at = datetime(2026, 10, 14, 10, 30, tzinfo=timezone.utc)

    with test_database() as session:
        session.add_all(
            [
                LocationRow(id=location_id, name="Lab Site A"),
                ZoneRow(
                    id=first_zone_id,
                    location_id=location_id,
                    name="Bench 1",
                    moisture_threshold_low=0.2,
                    moisture_threshold_high=0.45,
                ),
                ZoneRow(
                    id=empty_zone_id,
                    location_id=location_id,
                    name="Bench 2",
                    moisture_threshold_low=0.3,
                    moisture_threshold_high=0.6,
                ),
                DeviceRow(
                    id=assigned_device_id,
                    device_type="moisture_sensor",
                    role="sensor",
                    device_family="edge",
                    display_name="Bench moisture",
                    default_config={"protocol": "mqtt"},
                    sampling_interval_seconds=300,
                    tracking_enabled=True,
                    location_id=location_id,
                    zone_id=first_zone_id,
                ),
                DeviceRow(
                    id=unassigned_device_id,
                    device_type="moisture_sensor",
                    role="sensor",
                    device_family="edge",
                    display_name="Unassigned moisture",
                    default_config={"protocol": "mqtt"},
                    sampling_interval_seconds=60,
                    tracking_enabled=False,
                ),
                ReadingRow(
                    device_id=assigned_device_id,
                    value=0.31,
                    unit="vwc",
                    source="mqtt",
                    recorded_at=recorded_at,
                ),
            ]
        )
        session.commit()

    unknown_location_response = api_client.get(f"/api/locations/{uuid.uuid4()}/overview")
    assert unknown_location_response.status_code == 404

    response = api_client.get(f"/api/locations/{location_id}/overview")
    assert response.status_code == 200, response.text
    overview = response.json()

    assert overview["location"] == {"id": str(location_id), "name": "Lab Site A"}
    assert overview["strategy_key"] is None
    assert overview["last_recommendation"] is None
    assert overview["device_counts"] == {"sensor": 1, "actuator": 0}

    zones_by_id = {zone["id"]: zone for zone in overview["zones"]}
    assert set(zones_by_id) == {str(first_zone_id), str(empty_zone_id)}
    assert [device["id"] for device in zones_by_id[str(first_zone_id)]["devices"]] == [
        str(assigned_device_id)
    ]
    assert all(
        device["id"] != str(unassigned_device_id)
        for zone in overview["zones"]
        for device in zone["devices"]
    )

    first_zone = zones_by_id[str(first_zone_id)]
    assert first_zone["devices"][0] == {
        "id": str(assigned_device_id),
        "device_type": "moisture_sensor",
        "role": "sensor",
        "display_name": "Bench moisture",
    }
    assert first_zone["latest_readings"] == [
        {
            "device_id": str(assigned_device_id),
            "value": 0.31,
            "unit": "vwc",
            "recorded_at": recorded_at.isoformat(),
            "tracking_enabled": True,
            "sampling_interval_seconds": 300,
        }
    ]
    assert zones_by_id[str(empty_zone_id)]["devices"] == []
    assert zones_by_id[str(empty_zone_id)]["latest_readings"] == []

    save_response = api_client.put(
        f"/api/locations/{location_id}/automation",
        json={"strategy_key": "conservative"},
    )
    assert save_response.status_code == 200, save_response.text

    evaluated = api_client.post(f"/api/locations/{location_id}/automation/evaluate")
    assert evaluated.status_code == 200, evaluated.text
    overview_after_strategy = api_client.get(f"/api/locations/{location_id}/overview")
    assert overview_after_strategy.status_code == 200, overview_after_strategy.text
    recommendation = overview_after_strategy.json()["last_recommendation"]
    assert recommendation == {
        "action": evaluated.json()["action"],
        "reason": evaluated.json()["reason"],
    }
