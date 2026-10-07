from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.automation.context import LocationAutomationContext


@dataclass(frozen=True)
class Recommendation:
    action: str
    reason: str
    score: float | None = None


class AutomationStrategy(ABC):
    key: str

    @abstractmethod
    def decide(self, context: LocationAutomationContext) -> Recommendation:
        raise NotImplementedError


class ConservativeMoistureStrategy(AutomationStrategy):
    """Irrigate only when moisture falls below the zone's low threshold."""

    key = "conservative"

    def decide(self, context: LocationAutomationContext) -> Recommendation:
        if context.moisture is None:
            return Recommendation("wait", "No moisture sensor reading is available")

        if context.moisture < context.moisture_threshold_low:
            return Recommendation(
                "irrigate",
                f"Moisture {context.moisture:.2f} is below the low threshold "
                f"{context.moisture_threshold_low:.2f}",
            )

        return Recommendation(
            "wait",
            f"Moisture {context.moisture:.2f} has not fallen below the low "
            f"threshold {context.moisture_threshold_low:.2f}",
        )


class AggressiveMoistureStrategy(AutomationStrategy):
    """Irrigate as soon as moisture falls below the zone's high threshold."""

    key = "aggressive"

    def decide(self, context: LocationAutomationContext) -> Recommendation:
        if context.moisture is None:
            return Recommendation("wait", "No moisture sensor reading is available")

        if context.moisture < context.moisture_threshold_high:
            return Recommendation(
                "irrigate",
                f"Moisture {context.moisture:.2f} is below the high threshold "
                f"{context.moisture_threshold_high:.2f}",
            )

        return Recommendation(
            "wait",
            f"Moisture {context.moisture:.2f} is at or above the high threshold "
            f"{context.moisture_threshold_high:.2f}",
        )


_STRATEGIES: dict[str, AutomationStrategy] = {
    ConservativeMoistureStrategy.key: ConservativeMoistureStrategy(),
    AggressiveMoistureStrategy.key: AggressiveMoistureStrategy(),
}


def get_strategy(key: str) -> AutomationStrategy:
    try:
        return _STRATEGIES[key]
    except KeyError as error:
        raise ValueError(f"Unknown automation strategy: {key}") from error
