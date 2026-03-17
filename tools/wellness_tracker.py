"""Track wellness state for biohacking recommendations."""
from typing import Optional

class WellnessTracker:
    def from_manual(self, sleep_hours: float, sleep_quality: str,
                    energy_level: int, last_meal_hours_ago: float,
                    hydration: str, hrv: Optional[float] = None) -> dict:
        return {"sleep_hours": sleep_hours, "sleep_quality": sleep_quality, "hrv": hrv,
                "energy_level": energy_level, "last_meal_hours_ago": last_meal_hours_ago,
                "hydration": hydration}

    def from_wearable(self, device: str, **kwargs) -> dict:
        raise NotImplementedError(
            f"Wearable integration for '{device}' is planned for a future phase. "
            "Supported devices will include: Oura Ring, WHOOP, Garmin. Use from_manual() for now.")

    def calculate_intensity_modifier(self, state: dict) -> float:
        modifier = 1.0
        sleep = state.get("sleep_hours", 7)
        energy = state.get("energy_level", 7)
        quality = state.get("sleep_quality", "good")
        hydration = state.get("hydration", "adequate")
        if sleep < 5: modifier -= 0.4
        elif sleep < 6: modifier -= 0.25
        elif sleep < 7: modifier -= 0.1
        if quality == "poor": modifier -= 0.15
        elif quality == "fair": modifier -= 0.05
        if energy < 4: modifier -= 0.2
        elif energy < 6: modifier -= 0.1
        if hydration == "low": modifier -= 0.1
        return max(0.1, min(1.0, round(modifier, 2)))

    def generate_alerts(self, state: dict) -> list[str]:
        alerts = []
        if state.get("sleep_hours", 7) < 6:
            alerts.append("Low sleep detected — reduce new opening study, prioritize review")
        if state.get("energy_level", 7) < 5:
            alerts.append("Low energy — skip active calculation drills, focus on passive study")
        if state.get("hydration") == "low":
            alerts.append("Dehydration risk — drink water with electrolytes before studying")
        if state.get("last_meal_hours_ago", 0) > 4:
            alerts.append("Eat a balanced snack before starting — brain needs glucose")
        if state.get("sleep_quality") == "poor":
            alerts.append("Poor sleep quality — consider shorter study session with more breaks")
        return alerts
