import os
import uuid
from datetime import UTC, datetime, timedelta

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


def test_apply_and_list_actuator_executions(api_client: TestClient, test_database):
    from infrastructure.persistence.models import ActuatorStateRow, DeviceRow

    device_id = uuid.uuid4()
    stale_time = datetime.now(UTC) - timedelta(minutes=31)
    with test_database() as session:
        session.add(
            DeviceRow(
                id=device_id,
                device_type="water_pump",
                role="actuator",
                device_family="simulation",
                display_name="Test pump",
                default_config={},
                sampling_interval_seconds=300,
                tracking_enabled=True,
            )
        )
        session.add(
            ActuatorStateRow(
                device_id=device_id,
                state="running",
                updated_at=stale_time,
            )
        )
        session.commit()

    blocked = api_client.post(
        f"/api/actuators/{device_id}/apply",
        json={"command": "unknown_command"},
    )
    assert blocked.status_code == 200, blocked.text
    assert blocked.json() == {
        "success": False,
        "policy_applied": ["maxRunTime", "logging"],
        "message": "Max run time exceeded",
    }

    with test_database() as session:
        state = session.get(ActuatorStateRow, device_id)
        assert state is not None
        state.state = "idle"
        state.updated_at = datetime.now(UTC)
        session.commit()

    succeeded = api_client.post(
        f"/api/actuators/{device_id}/apply",
        json={"command": "unknown_command"},
    )
    assert succeeded.status_code == 200, succeeded.text
    assert succeeded.json() == {
        "success": True,
        "policy_applied": ["logging"],
        "message": None,
    }

    executions = api_client.get("/api/actuators/executions?limit=20")
    assert executions.status_code == 200, executions.text
    rows = executions.json()
    assert len(rows) == 2
    assert rows[0]["device_id"] == str(device_id)
    assert rows[0]["success"] is True
    assert rows[0]["policy_applied"] == ["logging"]
    assert rows[0]["message"] is None
    assert rows[1]["success"] is False
    assert rows[1]["policy_applied"] == ["maxRunTime", "logging"]
    assert rows[1]["message"] == "Max run time exceeded"
