import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from application.commands.dto import CommandLogDto, CommandRequestDto
from application.commands.service import CommandService, DeviceNotFoundError
from domain.commands.invoker import UnknownCommandError
from infrastructure.db import get_db
from infrastructure.persistence.command_log_repository import CommandLogRepository

router = APIRouter(prefix="/api/commands", tags=["commands"])


@router.post("", response_model=CommandLogDto)
def create_command(payload: CommandRequestDto, db: Session = Depends(get_db)):
    service = CommandService(db)
    try:
        row = service.execute(payload.device_id, payload.command_type, payload.payload)
    except DeviceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except UnknownCommandError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if row.status == "rejected":
        raise HTTPException(status_code=409, detail=CommandLogDto.model_validate(row).model_dump(mode="json"))
    if row.status in {"success", "failed"}:
        return row
    raise HTTPException(status_code=400, detail=f"Unsupported command status: {row.status}")


@router.get("", response_model=list[CommandLogDto])
def list_commands(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
):
    return [
        CommandLogDto.model_validate(row)
        for row in CommandLogRepository(db).list_recent(limit)
    ]
