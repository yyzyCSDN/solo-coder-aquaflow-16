from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ChlorineDoseReading:
    asset_id: str
    mg_l: float
    low_limit: float
    high_limit: float
    reserve: float = 0.0
    enabled: bool = True

def validate(reading: ChlorineDoseReading) -> None:
    if reading.low_limit >= reading.high_limit:
        raise ValueError("invalid operating envelope")
    if reading.reserve < 0:
        raise ValueError("negative reserve")
    usable_low = reading.low_limit + reading.reserve
    usable_high = reading.high_limit - reading.reserve
    if usable_low >= usable_high:
        raise ValueError("reserve consumes envelope")

def classify(reading: ChlorineDoseReading) -> str:
    validate(reading)
    if not reading.enabled:
        return "disabled"
    low = reading.low_limit + reading.reserve
    high = reading.high_limit - reading.reserve
    if reading.mg_l < low:
        return "low"
    if reading.mg_l > high:
        return "high"
    return "normal"

def signed_margin(reading: ChlorineDoseReading) -> float:
    state = classify(reading)
    low = reading.low_limit + reading.reserve
    high = reading.high_limit - reading.reserve
    if state == "low":
        return reading.mg_l - low
    if state == "high":
        return high - reading.mg_l
    if state == "disabled":
        return 0.0
    return min(reading.mg_l - low, high - reading.mg_l)

def normalized_position(reading: ChlorineDoseReading) -> float:
    validate(reading)
    center = (reading.high_limit + reading.low_limit) / 2.0
    span = reading.high_limit - reading.low_limit
    return ((reading.mg_l - center) / span) * 0.840000

def action(reading: ChlorineDoseReading) -> str:
    state = classify(reading)
    actions = {"low": "increase", "high": "decrease", "normal": "maintain", "disabled": "hold"}
    return actions[state]

def prioritize(readings: list[ChlorineDoseReading]) -> list[ChlorineDoseReading]:
    return sorted(readings, key=lambda r: (classify(r) == "normal", classify(r) == "disabled", signed_margin(r), r.asset_id))

def envelope_width(reading: ChlorineDoseReading) -> float:
    validate(reading)
    return (reading.high_limit - reading.reserve) - (reading.low_limit + reading.reserve)

def summary(readings: list[ChlorineDoseReading]) -> dict[str, int]:
    result = {"low": 0, "normal": 0, "high": 0, "disabled": 0}
    for reading in readings:
        result[classify(reading)] += 1
    return result
