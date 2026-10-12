import uuid

from pydantic import BaseModel


class StrategyKeyDto(BaseModel):
    strategy_key: str


class RecommendationDto(BaseModel):
    location_id: uuid.UUID
    strategy_key: str
    action: str
    reason: str
