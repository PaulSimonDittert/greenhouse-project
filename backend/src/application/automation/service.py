import uuid

from sqlalchemy.orm import Session

from application.automation.dto import RecommendationDto
from domain.automation.context import LocationAutomationContext
from domain.automation.strategy import get_strategy
from infrastructure.persistence.automation_repository import AutomationRuleRepository


class AutomationService:
    def __init__(self, db: Session):
        self.db = db
        self._repo = AutomationRuleRepository(db)

    def set_strategy(self, location_id: uuid.UUID, strategy_key: str) -> str:
        self._require_location(location_id)
        strategy = get_strategy(strategy_key)
        self._repo.upsert_for_location(location_id, strategy.key)
        return strategy.key

    def evaluate(self, location_id: uuid.UUID) -> RecommendationDto:
        location = self._require_location(location_id)
        rule = self._repo.get_for_location(location_id)
        strategy_key = rule.strategy_key if rule else "conservative"
        strategy = get_strategy(strategy_key)

        zone_config = self._repo.get_location_config(location_id)
        if zone_config is None:
            raise ValueError("Location not found")

        _, zone_rows = zone_config
        if not zone_rows:
            raise ValueError("Location has no zones configured")

        selected_recommendation = None
        for zone in zone_rows:
            moisture = self._repo.get_zone_moisture(zone.id)
            context = LocationAutomationContext(
                location_id=location.id,
                zone_id=zone.id,
                moisture=moisture,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
            )
            recommendation = strategy.decide(context)
            if recommendation.action == "irrigate":
                selected_recommendation = recommendation
                break
            if selected_recommendation is None:
                selected_recommendation = recommendation

        if selected_recommendation is None:
            raise ValueError("Location has no zones configured")

        return RecommendationDto(
            location_id=location.id,
            strategy_key=strategy_key,
            action=selected_recommendation.action,
            reason=selected_recommendation.reason,
        )

    def _require_location(self, location_id: uuid.UUID):
        location = self._repo.get_location_config(location_id)
        if location is None:
            raise ValueError("Location not found")
        return location[0]
