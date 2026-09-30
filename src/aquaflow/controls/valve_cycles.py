from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ValveCyclesReading:
    asset_id: str
    count: float
    low_limit: float
    high_limit: float
    reserve: float = 0.0
    enabled: bool = True

def validate(reading: ValveCyclesReading) -> None:
    if reading.low_limit >= reading.high_limit:
        raise ValueError("invalid operating envelope")
    if reading.reserve < 0:
        raise ValueError("negative reserve")
    usable_low = reading.low_limit + reading.reserve
    usable_high = reading.high_limit - reading.reserve
    if usable_low >= usable_high:
        raise ValueError("reserve consumes envelope")

def classify(reading: ValveCyclesReading) -> str:
    validate(reading)
    if not reading.enabled:
        return "disabled"
    low = reading.low_limit + reading.reserve
    high = reading.high_limit - reading.reserve
    if reading.count < low:
        return "low"
    if reading.count > high:
        return "high"
    return "normal"

def signed_margin(reading: ValveCyclesReading) -> float:
    state = classify(reading)
    low = reading.low_limit + reading.reserve
    high = reading.high_limit - reading.reserve
    if state == "low":
        return reading.count - low
    if state == "high":
        return high - reading.count
    if state == "disabled":
        return 0.0
    return min(reading.count - low, high - reading.count)

def normalized_position(reading: ValveCyclesReading) -> float:
    validate(reading)
    center = (reading.high_limit + reading.low_limit) / 2.0
    span = reading.high_limit - reading.low_limit
    return ((reading.count - center) / span) * 1.290000

def action(reading: ValveCyclesReading) -> str:
    state = classify(reading)
    actions = {"low": "increase", "high": "decrease", "normal": "maintain", "disabled": "hold"}
    return actions[state]

def prioritize(readings: list[ValveCyclesReading]) -> list[ValveCyclesReading]:
    return sorted(readings, key=lambda r: (classify(r) == "normal", classify(r) == "disabled", signed_margin(r), r.asset_id))

def envelope_width(reading: ValveCyclesReading) -> float:
    validate(reading)
    return (reading.high_limit - reading.reserve) - (reading.low_limit + reading.reserve)

def summary(readings: list[ValveCyclesReading]) -> dict[str, int]:
    result = {"low": 0, "normal": 0, "high": 0, "disabled": 0}
    for reading in readings:
        result[classify(reading)] += 1
    return result
