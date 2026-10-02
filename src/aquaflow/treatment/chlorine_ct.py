"""Chlorine disinfection CT credit with temperature compensation.

CT credit is expressed against the 20 °C reference condition.  Disinfection
kinetics roughly double every 10 °C, so each contact segment is corrected by
``2 ** ((temperature_c - 20) / 10)``: cold water earns less credit, warm water
more, and a segment measured at the reference temperature keeps a factor of
exactly 1.0.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

REFERENCE_TEMPERATURE_C = 20.0


@dataclass(frozen=True)
class Segment:
    minutes: float
    residual: float
    baffling: float
    temperature_c: float


def temperature_factor(temperature_c: float) -> float:
    """Temperature correction against the 20 °C reference (doubles / 10 °C)."""
    return 2.0 ** ((float(temperature_c) - REFERENCE_TEMPERATURE_C) / 10.0)


def _validated(segment: Segment) -> Segment:
    minutes = float(segment.minutes)
    residual = float(segment.residual)
    baffling = float(segment.baffling)
    temperature = float(segment.temperature_c)
    if minutes <= 0:
        raise ValueError("invalid segment: contact time must be positive")
    if residual < 0:
        raise ValueError("invalid segment: residual must be non-negative")
    if not 0.0 < baffling <= 1.0:
        raise ValueError("invalid segment: baffling factor must be within (0, 1]")
    if not math.isfinite(temperature) or not 0.0 < temperature < 100.0:
        raise ValueError("invalid segment: temperature must be liquid water in (0, 100) °C")
    return Segment(minutes, residual, baffling, temperature)


def segment_ct(segment: Segment) -> float:
    """Temperature-compensated CT credit of one contact segment."""
    s = _validated(segment)
    return s.minutes * s.residual * s.baffling * temperature_factor(s.temperature_c)


def effective_ct(rows: list[Segment]) -> float:
    return sum(segment_ct(r) for r in rows)


def compliant(rows, required):
    return required > 0 and effective_ct(rows) >= required
