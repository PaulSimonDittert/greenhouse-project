import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from application.devices.actuator_execution_service import (
    ActuatorDeviceNotFoundError,
    ActuatorExecutionService,
)
from application.devices.dto import (
    ActuatorApplyRequest,
    ActuatorApplyResultDto,
    ActuatorExecutionDto,
)
from infrastructure.db import get_db

router = APIRouter(prefix="/api/actuators", tags=["actuators"])


@router.get("/executions", response_model=list[ActuatorExecutionDto])
def list_actuator_executions(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=20, ge=1, le=100),
):
    return ActuatorExecutionService(db).list_recent(limit)


@router.post("/{device_id}/apply", response_model=ActuatorApplyResultDto)
def apply_actuator_command(
    device_id: uuid.UUID,
    payload: ActuatorApplyRequest,
    db: Annotated[Session, Depends(get_db)],
):
    service = ActuatorExecutionService(db)
    try:
        return service.apply(device_id, payload.command, payload.payload)
    except ActuatorDeviceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
