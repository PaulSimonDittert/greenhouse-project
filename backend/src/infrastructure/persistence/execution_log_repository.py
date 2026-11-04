import uuid

from sqlalchemy.orm import Session

from infrastructure.persistence.models import ActuatorExecutionLogRow


class ActuatorExecutionLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        *,
        device_id: uuid.UUID,
        success: bool,
        policy_applied: list[str],
        message: str | None = None,
    ) -> ActuatorExecutionLogRow:
        row = ActuatorExecutionLogRow(
            device_id=device_id,
            success=success,
            policy_applied=list(policy_applied),
            message=message,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_recent(self, limit: int = 20) -> list[ActuatorExecutionLogRow]:
        return (
            self.db.query(ActuatorExecutionLogRow)
            .order_by(ActuatorExecutionLogRow.created_at.desc())
            .limit(limit)
            .all()
        )
