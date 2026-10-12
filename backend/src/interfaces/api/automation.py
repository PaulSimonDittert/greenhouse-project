import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.automation.dto import RecommendationDto, StrategyKeyDto
from application.automation.service import AutomationService
from infrastructure.db import get_db

router = APIRouter(prefix="/api/locations", tags=["automation"])


@router.put("/{location_id}/automation", response_model=StrategyKeyDto)
def save_location_strategy(
    location_id: uuid.UUID,
    payload: StrategyKeyDto,
    db: Session = Depends(get_db),
):
    service = AutomationService(db)
    try:
        strategy_key = service.set_strategy(location_id, payload.strategy_key)
        return StrategyKeyDto(strategy_key=strategy_key)
    except ValueError as exc:
        message = str(exc)
        if "Location not found" in message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.post("/{location_id}/automation/evaluate", response_model=RecommendationDto)
def evaluate_location_strategy(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = AutomationService(db)
    try:
        return service.evaluate(location_id)
    except ValueError as exc:
        message = str(exc)
        if "Location not found" in message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
