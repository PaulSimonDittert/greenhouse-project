import uuid

from sqlalchemy.orm import Session

from domain.actuators.state import VALID_STATES
from infrastructure.persistence.models import ActuatorStateRow


class ActuatorStateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_for_device(self, device_id: uuid.UUID) -> str | None:
        row = self.db.query(ActuatorStateRow).filter(ActuatorStateRow.device_id == device_id).one_or_none()
        if row is None:
            return None
        return row.state

    def ensure_for_device(self, device_id: uuid.UUID, *, default_state: str = "idle") -> str:
        if default_state not in VALID_STATES:
            raise ValueError(f"Unknown actuator state: {default_state}")

        row = self.db.query(ActuatorStateRow).filter(ActuatorStateRow.device_id == device_id).one_or_none()
        if row is None:
            row = ActuatorStateRow(device_id=device_id, state=default_state)
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
        return row.state

    def save(self, device_id: uuid.UUID, state: str) -> str:
        if state not in VALID_STATES:
            raise ValueError(f"Unknown actuator state: {state}")

        row = self.db.query(ActuatorStateRow).filter(ActuatorStateRow.device_id == device_id).one_or_none()
        if row is None:
            row = ActuatorStateRow(device_id=device_id, state=state)
            self.db.add(row)
        else:
            row.state = state

        self.db.commit()
        self.db.refresh(row)
        return row.state

    def list_for_devices(self, device_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
        if not device_ids:
            return {}
        rows = self.db.query(ActuatorStateRow).filter(ActuatorStateRow.device_id.in_(device_ids)).all()
        return {row.device_id: row.state for row in rows}
