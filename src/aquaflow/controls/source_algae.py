from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SourceAlgaeReading:
    asset_id: str
    cells_ml: float
    low_limit: float
    high_limit: float
    reserve: float = 0.0
    enabled: bool = True

def validate(reading: SourceAlgaeReading) -> None:
    if reading.low_limit >= reading.high_limit:
        raise ValueError("invalid operating envelope")
    if reading.reserve < 0:
        raise ValueError("negative reserve")
    if reading.low_limit + reading.reserve >= reading.high_limit - reading.reserve:
        raise ValueError("reserve consumes envelope")

def classify(reading: SourceAlgaeReading) -> str:
    validate(reading)
    if not reading.enabled:
        return "disabled"
    low = reading.low_limit + reading.reserve
    high = reading.high_limit - reading.reserve
    if reading.cells_ml < low:
        return "low"
    if reading.cells_ml > high:
        return "high"
    return "normal"

def margin(reading: SourceAlgaeReading) -> float:
    state = classify(reading)
    if state != "normal":
        return 0.0
    low = reading.low_limit + reading.reserve
    high = reading.high_limit - reading.reserve
    return min(reading.cells_ml - low, high - reading.cells_ml)

def normalized_position(reading: SourceAlgaeReading) -> float:
    validate(reading)
    center = (reading.high_limit + reading.low_limit) / 2.0
    span = reading.high_limit - reading.low_limit
    return ((reading.cells_ml - center) / span) * 1.400000

def requires_action(reading: SourceAlgaeReading) -> bool:
    return classify(reading) in {"low", "high"}

def action(reading: SourceAlgaeReading) -> str:
    state = classify(reading)
    if state == "low":
        return "increase"
    if state == "high":
        return "decrease"
    if state == "disabled":
        return "hold"
    return "maintain"

def prioritize(readings: list[SourceAlgaeReading]) -> list[SourceAlgaeReading]:
    return sorted(
        readings,
        key=lambda r: (
            classify(r) == "normal",
            classify(r) == "disabled",
            margin(r),
            r.asset_id,
        ),
    )

def summary(readings: list[SourceAlgaeReading]) -> dict[str, int]:
    result = {"low": 0, "normal": 0, "high": 0, "disabled": 0}
    for reading in readings:
        result[classify(reading)] += 1
    return result
