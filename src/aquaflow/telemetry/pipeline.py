from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from statistics import median

@dataclass(frozen=True)
class Reading:
    device: str
    at: datetime
    value: float
    sequence: int
    quality: float = 1.0

@dataclass(frozen=True)
class Calibration:
    device: str
    starts: datetime
    ends: datetime | None
    slope: float
    intercept: float


def calibration_at(device: str, at: datetime, rows: list[Calibration]) -> Calibration | None:
    t = at.astimezone(timezone.utc)
    candidates = []
    for row in rows:
        if row.device != device:
            continue
        start = row.starts.astimezone(timezone.utc)
        end = row.ends.astimezone(timezone.utc) if row.ends else None
        if start <= t and (end is None or t < end):
            candidates.append(row)
    if len(candidates) > 1:
        raise ValueError('overlapping calibrations')
    return candidates[0] if candidates else None


def calibrated(reading: Reading, calibrations: list[Calibration]) -> Reading:
    cal = calibration_at(reading.device, reading.at, calibrations)
    if cal is None:
        return reading
    return Reading(reading.device, reading.at, reading.value * cal.slope + cal.intercept, reading.sequence, reading.quality)


def deduplicate(rows: list[Reading]) -> list[Reading]:
    by_key = {}
    for row in rows:
        key = (row.device, row.sequence)
        existing = by_key.get(key)
        if existing is None or row.quality > existing.quality:
            by_key[key] = row
        elif row.quality == existing.quality and row.at < existing.at:
            by_key[key] = row
    return sorted(by_key.values(), key=lambda r: (r.device, r.at, r.sequence))


def device_watermarks(rows: list[Reading], allowed_lateness: timedelta) -> dict[str, datetime]:
    latest = {}
    for row in rows:
        t = row.at.astimezone(timezone.utc)
        if row.device not in latest or t > latest[row.device]:
            latest[row.device] = t
    return {device: t - allowed_lateness for device, t in latest.items()}


def ready_by_watermark(rows: list[Reading], allowed_lateness: timedelta) -> list[Reading]:
    marks = device_watermarks(rows, allowed_lateness)
    return sorted([r for r in rows if r.at.astimezone(timezone.utc) <= marks[r.device]], key=lambda r: (r.at, r.sequence))


def gaps(rows: list[Reading], expected: timedelta, tolerance: float = 0.25) -> dict[str, list[tuple[datetime, datetime]]]:
    if expected.total_seconds() <= 0 or tolerance < 0:
        raise ValueError('invalid gap policy')
    grouped = defaultdict(list)
    for row in deduplicate(rows):
        grouped[row.device].append(row)
    threshold = expected.total_seconds() * (1 + tolerance)
    result = {}
    for device, device_rows in grouped.items():
        missing = []
        for a, b in zip(device_rows, device_rows[1:]):
            if (b.at - a.at).total_seconds() > threshold:
                missing.append((a.at, b.at))
        result[device] = missing
    return result


def rolling_mean(rows: list[Reading], window: timedelta, at: datetime, device: str) -> float | None:
    start = at - window
    values = [r.value for r in rows if r.device == device and start < r.at <= at and r.quality >= 0.5]
    return None if not values else sum(values) / len(values)


def rolling_median(rows: list[Reading], window: timedelta, at: datetime, device: str) -> float | None:
    start = at - window
    values = [r.value for r in rows if r.device == device and start < r.at <= at and r.quality >= 0.5]
    return None if not values else median(values)


def resample(rows: list[Reading], device: str, start: datetime, end: datetime, step: timedelta) -> list[tuple[datetime, float | None]]:
    if step.total_seconds() <= 0 or end <= start:
        raise ValueError('invalid resample window')
    source = sorted([r for r in rows if r.device == device], key=lambda r: r.at)
    result = []
    cursor = start
    while cursor <= end:
        previous = [r for r in source if r.at <= cursor]
        following = [r for r in source if r.at >= cursor]
        value = None
        if previous and following:
            a = previous[-1]
            b = following[0]
            if a.at == b.at:
                value = a.value
            else:
                fraction = (cursor - a.at).total_seconds() / (b.at - a.at).total_seconds()
                value = a.value + fraction * (b.value - a.value)
        result.append((cursor, value))
        cursor += step
    return result


def completeness(rows: list[Reading], device: str, start: datetime, end: datetime, expected: timedelta) -> float:
    if end <= start or expected.total_seconds() <= 0:
        raise ValueError('invalid completeness window')
    expected_count = int((end - start).total_seconds() // expected.total_seconds()) + 1
    observed = len({r.at for r in rows if r.device == device and start <= r.at <= end})
    return min(1.0, observed / max(1, expected_count))


def robust_outliers(rows: list[Reading], device: str, threshold: float = 6.0) -> list[Reading]:
    values = [r.value for r in rows if r.device == device and r.quality >= 0.5]
    if len(values) < 3:
        return []
    center = median(values)
    mad = median(abs(v - center) for v in values)
    if mad == 0:
        return [r for r in rows if r.device == device and r.value != center]
    return [r for r in rows if r.device == device and abs(r.value - center) / mad > threshold]


def summarize_device(rows: list[Reading], device: str) -> dict[str, float | int | None]:
    values = [r.value for r in rows if r.device == device]
    if not values:
        return {'count': 0, 'min': None, 'max': None, 'mean': None}
    return {'count': len(values), 'min': min(values), 'max': max(values), 'mean': sum(values) / len(values)}
