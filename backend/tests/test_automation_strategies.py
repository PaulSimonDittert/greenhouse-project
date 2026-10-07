import uuid

import pytest

from domain.automation.context import LocationAutomationContext
from domain.automation.strategy import (
    AggressiveMoistureStrategy,
    ConservativeMoistureStrategy,
    get_strategy,
)


@pytest.fixture
def within_band_context() -> LocationAutomationContext:
    return LocationAutomationContext(
        location_id=uuid.uuid4(),
        zone_id=uuid.uuid4(),
        moisture=0.4,
        moisture_threshold_low=0.25,
        moisture_threshold_high=0.45,
    )


def test_conservative_waits_when_moisture_is_within_band(
    within_band_context: LocationAutomationContext,
) -> None:
    result = ConservativeMoistureStrategy().decide(within_band_context)

    assert result.action == "wait"


def test_aggressive_differs_on_same_context(
    within_band_context: LocationAutomationContext,
) -> None:
    conservative = ConservativeMoistureStrategy().decide(within_band_context)
    aggressive = AggressiveMoistureStrategy().decide(within_band_context)

    assert conservative.action == "wait"
    assert aggressive.action == "irrigate"


def test_both_strategies_wait_without_a_moisture_reading(
    within_band_context: LocationAutomationContext,
) -> None:
    context_without_reading = LocationAutomationContext(
        location_id=within_band_context.location_id,
        zone_id=within_band_context.zone_id,
        moisture=None,
        moisture_threshold_low=within_band_context.moisture_threshold_low,
        moisture_threshold_high=within_band_context.moisture_threshold_high,
    )

    assert ConservativeMoistureStrategy().decide(context_without_reading).action == "wait"
    assert AggressiveMoistureStrategy().decide(context_without_reading).action == "wait"


def test_get_strategy_rejects_unknown_keys() -> None:
    with pytest.raises(ValueError, match="Unknown automation strategy"):
        get_strategy("unknown")
