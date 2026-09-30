from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PrvSetpointReading:
    asset_id: str
    kpa: float
    low_limit: float
    high_limit: float
    reserve: float = 0.0
    enabled: bool = True

def validate(reading: PrvSetpointReading) -> None:
    if reading.low_limit >= reading.high_limit:
        raise ValueError("invalid operating envelope")
    if reading.reserve < 0:
        raise ValueError("negative reserve")
    usable_low = reading.low_limit + reading.reserve
    usable_high = reading.high_limit - reading.reserve
    if usable_low >= usable_high:
        raise ValueError("reserve consumes envelope")

def classify(reading: PrvSetpointReading) -> str:
    validate(reading)
    if not reading.enabled:
        return "disabled"
    low = reading.low_limit + reading.reserve
    high = reading.high_limit - reading.reserve
    if reading.kpa < low:
        return "low"
    if reading.kpa > high:
        return "high"
    return "normal"

def signed_margin(reading: PrvSetpointReading) -> float:
    state = classify(reading)
    low = reading.low_limit + reading.reserve
    high = reading.high_limit - reading.reserve
    if state == "low":
        return reading.kpa - low
    if state == "high":
        return high - reading.kpa
    if state == "disabled":
        return 0.0
    return min(reading.kpa - low, high - reading.kpa)

def normalized_position(reading: PrvSetpointReading) -> float:
    validate(reading)
    center = (reading.high_limit + reading.low_limit) / 2.0
    span = reading.high_limit - reading.low_limit
    return ((reading.kpa - center) / span) * 1.090000

def action(reading: PrvSetpointReading) -> str:
    state = classify(reading)
    actions = {"low": "increase", "high": "decrease", "normal": "maintain", "disabled": "hold"}
    return actions[state]

def prioritize(readings: list[PrvSetpointReading]) -> list[PrvSetpointReading]:
    return sorted(readings, key=lambda r: (classify(r) == "normal", classify(r) == "disabled", signed_margin(r), r.asset_id))

def envelope_width(reading: PrvSetpointReading) -> float:
    validate(reading)
    return (reading.high_limit - reading.reserve) - (reading.low_limit + reading.reserve)

def summary(readings: list[PrvSetpointReading]) -> dict[str, int]:
    result = {"low": 0, "normal": 0, "high": 0, "disabled": 0}
    for reading in readings:
        result[classify(reading)] += 1
    return result
