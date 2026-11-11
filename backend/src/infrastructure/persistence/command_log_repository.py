import uuid

from sqlalchemy.orm import Session

from infrastructure.persistence.models import CommandLogRow


class CommandLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        *,
        command_type: str,
        device_id: uuid.UUID,
        payload: dict | None = None,
        status: str = "success",
        error_message: str | None = None,
    ) -> CommandLogRow:
        row = CommandLogRow(
            command_type=command_type,
            device_id=device_id,
            payload=payload,
            status=status,
            error_message=error_message,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_recent(self, limit: int = 50) -> list[CommandLogRow]:
        return (
            self.db.query(CommandLogRow)
            .order_by(CommandLogRow.created_at.desc())
            .limit(limit)
            .all()
        )
