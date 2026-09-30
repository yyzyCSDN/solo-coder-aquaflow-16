from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from aquaflow.network.isolation import Pipe, isolated
from aquaflow.outage.impact import Customer, summarize
from aquaflow.leak.localize import Signal, rank as rank_leaks
from aquaflow.treatment.chlorine_ct import Segment, effective_ct

@dataclass(frozen=True)
class IsolationOption:
    valves: frozenset[str]
    isolated_nodes: frozenset[str]
    accounts: int
    population: int
    critical: int

@dataclass(frozen=True)
class WaterQualitySnapshot:
    at: datetime
    chlorine_ct: float
    turbidity_ntu: float
    pressure_min_kpa: float
    active_incidents: int

@dataclass(frozen=True)
class ControlDecision:
    priority: int
    category: str
    message: str
    evidence: tuple[str, ...]


def evaluate_isolation(nodes: set[str], pipes: list[Pipe], sources: set[str], valves: set[str], customers: list[Customer]) -> IsolationOption:
    cut = isolated(nodes, pipes, valves, sources)
    impact = summarize(customers, cut)
    return IsolationOption(
        frozenset(valves),
        frozenset(cut),
        impact["accounts"],
        impact["population"],
        impact["critical"],
    )


def best_isolation(options: list[set[str]], nodes: set[str], pipes: list[Pipe], sources: set[str], customers: list[Customer]) -> IsolationOption:
    if not options:
        raise ValueError("isolation options required")
    evaluated = [evaluate_isolation(nodes, pipes, sources, option, customers) for option in options]
    return min(
        evaluated,
        key=lambda option: (
            option.critical,
            option.population,
            option.accounts,
            len(option.valves),
            tuple(sorted(option.valves)),
        ),
    )


def quality_snapshot(at: datetime, ct_segments: list[Segment], turbidity_ntu: float, pressure_values: list[float], active_incidents: int) -> WaterQualitySnapshot:
    if turbidity_ntu < 0:
        raise ValueError("negative turbidity")
    if not pressure_values:
        raise ValueError("pressure values required")
    if active_incidents < 0:
        raise ValueError("negative incident count")
    return WaterQualitySnapshot(
        at,
        effective_ct(ct_segments),
        turbidity_ntu,
        min(pressure_values),
        active_incidents,
    )


def operational_decisions(snapshot: WaterQualitySnapshot, required_ct: float, turbidity_limit: float, pressure_minimum: float) -> list[ControlDecision]:
    decisions = []
    if snapshot.chlorine_ct < required_ct:
        decisions.append(ControlDecision(1, "disinfection", "increase disinfectant contact protection", (f"ct={snapshot.chlorine_ct:.3f}", f"required={required_ct:.3f}")))
    if snapshot.turbidity_ntu > turbidity_limit:
        decisions.append(ControlDecision(1, "turbidity", "hold affected treatment train and inspect filtration", (f"ntu={snapshot.turbidity_ntu:.3f}", f"limit={turbidity_limit:.3f}")))
    if snapshot.pressure_min_kpa < pressure_minimum:
        decisions.append(ControlDecision(2, "pressure", "investigate pressure loss and verify supply paths", (f"min_kpa={snapshot.pressure_min_kpa:.3f}", f"required={pressure_minimum:.3f}")))
    if snapshot.active_incidents >= 3:
        decisions.append(ControlDecision(2, "coordination", "activate consolidated incident command", (f"active_incidents={snapshot.active_incidents}",)))
    if not decisions:
        decisions.append(ControlDecision(5, "normal", "continue standard monitoring", (snapshot.at.isoformat(),)))
    return sorted(decisions, key=lambda row: (row.priority, row.category, row.message))


def leak_dispatch(signals: list[Signal], available_crews: int, minimum_score: float) -> list[str]:
    if available_crews < 0:
        raise ValueError("negative crew count")
    ranked = rank_leaks(signals)
    return [pipe for pipe, score in ranked if score >= minimum_score][:available_crews]


def escalation_deadline(opened: datetime, priority: int) -> datetime:
    if priority < 1 or priority > 5:
        raise ValueError("priority outside 1..5")
    minutes = {1: 10, 2: 30, 3: 60, 4: 240, 5: 480}[priority]
    return opened + timedelta(minutes=minutes)


def dashboard(snapshot: WaterQualitySnapshot, decisions: list[ControlDecision]) -> dict[str, object]:
    return {
        "at": snapshot.at.isoformat(),
        "chlorine_ct": snapshot.chlorine_ct,
        "turbidity_ntu": snapshot.turbidity_ntu,
        "pressure_min_kpa": snapshot.pressure_min_kpa,
        "active_incidents": snapshot.active_incidents,
        "decision_count": len(decisions),
        "highest_priority": min((d.priority for d in decisions), default=None),
        "categories": sorted({d.category for d in decisions}),
    }
