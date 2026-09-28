import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TEST_DATABASE_URL, reason="Set TEST_DATABASE_URL to an isolated PostgreSQL test database")


@pytest.fixture
def api_client():
    from infrastructure.db import get_db
    from infrastructure.persistence.models import Base
    from main import app

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    testing_sessions = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        with testing_sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(engine)
        engine.dispose()


def create_location(client: TestClient, name: str, zone_names: tuple[str, ...] = ("Bed",)) -> dict:
    response = client.post(
        "/api/locations/config",
        json={
            "location_name": name,
            "zones": [
                {
                    "name": zone_name,
                    "moisture_threshold_low": 0.25,
                    "moisture_threshold_high": 0.65,
                    "schedule": {"days": ["Mon", "Thu"]},
                }
                for zone_name in zone_names
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def provision_devices(client: TestClient) -> list[dict]:
    response = client.post("/api/devices/provision?family=simulation")
    assert response.status_code == 201, response.text
    return response.json()


def assign_device(client: TestClient, device_id: str, zone_id: str | None) -> None:
    response = client.patch(f"/api/devices/{device_id}/zone", json={"zone_id": zone_id})
    assert response.status_code == 200, response.text


def test_create_and_get_location_config_persists_location_and_zones(api_client: TestClient):
    created = create_location(api_client, "Greenhouse A", ("North", "South"))
    location_id = created["location"]["id"]

    response = api_client.get(f"/api/locations/{location_id}/config")

    assert response.status_code == 200
    config = response.json()
    assert config["location"]["id"] == location_id
    assert {zone["name"] for zone in config["zones"]} == {"North", "South"}
    assert all(zone["location_id"] == location_id for zone in config["zones"])
    assert config["zones"][0]["schedule"] == {"days": ["Mon", "Thu"]}


def test_invalid_location_payload_returns_400(api_client: TestClient):
    response = api_client.post(
        "/api/locations/config",
        json={
            "location_name": "Greenhouse A",
            "zones": [{"name": "Bed", "moisture_threshold_low": 0.8, "moisture_threshold_high": 0.4}],
        },
    )

    assert response.status_code == 400
    assert "strictly less" in response.json()["detail"]


def test_assign_devices_to_zone_zone_list_is_exclusive(api_client: TestClient):
    config = create_location(api_client, "Greenhouse A", ("North", "South"))
    devices = provision_devices(api_client)
    north_id, south_id = [zone["id"] for zone in config["zones"]]
    assign_device(api_client, devices[0]["id"], north_id)
    assign_device(api_client, devices[1]["id"], north_id)
    assign_device(api_client, devices[2]["id"], south_id)

    response = api_client.get(f"/api/locations/{config['location']['id']}/zones/{north_id}/devices")

    assert response.status_code == 200
    assert {device["id"] for device in response.json()} == {devices[0]["id"], devices[1]["id"]}
    assert devices[2]["id"] not in {device["id"] for device in response.json()}


def test_unassign_clears_zone_and_location(api_client: TestClient):
    config = create_location(api_client, "Greenhouse A")
    device = provision_devices(api_client)[0]
    assign_device(api_client, device["id"], config["zones"][0]["id"])
    assign_device(api_client, device["id"], None)

    response = api_client.get("/api/devices?family=simulation")
    unassigned = next(item for item in response.json() if item["id"] == device["id"])

    assert unassigned["zone_id"] is None
    assert unassigned["location_id"] is None


def test_list_locations_and_delete_clears_assignments(api_client: TestClient):
    first = create_location(api_client, "Greenhouse A")
    second = create_location(api_client, "Greenhouse B")
    device = provision_devices(api_client)[0]
    assign_device(api_client, device["id"], first["zones"][0]["id"])

    listed = api_client.get("/api/locations")
    assert {location["id"] for location in listed.json()} == {first["location"]["id"], second["location"]["id"]}

    deleted = api_client.delete(f"/api/locations/{first['location']['id']}")
    remaining = api_client.get("/api/locations")
    devices_after_delete = api_client.get("/api/devices?family=simulation").json()
    unassigned = next(item for item in devices_after_delete if item["id"] == device["id"])

    assert deleted.status_code == 204
    assert [location["id"] for location in remaining.json()] == [second["location"]["id"]]
    assert api_client.get(f"/api/locations/{first['location']['id']}/config").status_code == 404
    assert unassigned["zone_id"] is None
    assert unassigned["location_id"] is None


def test_add_update_and_delete_zone_clears_assignments(api_client: TestClient):
    config = create_location(api_client, "Greenhouse A", ("North", "South"))
    location_id = config["location"]["id"]
    device = provision_devices(api_client)[0]
    assign_device(api_client, device["id"], config["zones"][0]["id"])

    added = api_client.post(
        f"/api/locations/{location_id}/zones",
        json={"name": "East", "moisture_threshold_low": 0.2, "moisture_threshold_high": 0.6},
    )
    assert added.status_code == 201
    saved_config = api_client.get(f"/api/locations/{location_id}/config").json()
    assert "East" in {zone["name"] for zone in saved_config["zones"]}

    valid_update = api_client.patch(
        f"/api/locations/{location_id}/zones/{added.json()['id']}",
        json={
            "name": "East veranda",
            "moisture_threshold_low": 0.3,
            "moisture_threshold_high": 0.7,
            "schedule": {"days": ["Tue"]},
        },
    )
    assert valid_update.status_code == 200
    assert valid_update.json()["name"] == "East veranda"

    invalid_update = api_client.patch(
        f"/api/locations/{location_id}/zones/{added.json()['id']}",
        json={"name": "East veranda", "moisture_threshold_low": 0.9, "moisture_threshold_high": 0.1},
    )
    assert invalid_update.status_code == 400

    deleted = api_client.delete(f"/api/locations/{location_id}/zones/{config['zones'][0]['id']}")
    devices_after_delete = api_client.get("/api/devices?family=simulation").json()
    unassigned = next(item for item in devices_after_delete if item["id"] == device["id"])

    assert deleted.status_code == 204
    assert unassigned["zone_id"] is None
    assert unassigned["location_id"] is None


def test_delete_last_zone_is_rejected(api_client: TestClient):
    config = create_location(api_client, "Greenhouse A")
    location_id = config["location"]["id"]

    response = api_client.delete(f"/api/locations/{location_id}/zones/{config['zones'][0]['id']}")

    assert response.status_code == 400
    assert "last remaining zone" in response.json()["detail"]