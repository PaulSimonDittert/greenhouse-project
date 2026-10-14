import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.overview.dto import LocationOverviewDto
from application.overview.facade import LocationOverviewFacade
from infrastructure.db import get_db

router = APIRouter(prefix="/api/locations", tags=["overview"])


@router.get("/{location_id}/overview", response_model=LocationOverviewDto)
def get_location_overview(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    facade = LocationOverviewFacade(db)
    try:
        return facade.get_overview(location_id)
    except ValueError as exc:
        message = str(exc)
        if "Location not found" in message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc
