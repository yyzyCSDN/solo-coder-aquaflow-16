from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict, deque
from heapq import heappush, heappop

@dataclass(frozen=True)
class Junction:
    node_id: str
    elevation_m: float
    demand_l_s: float
    source: bool = False
    critical: bool = False

@dataclass(frozen=True)
class Main:
    main_id: str
    a: str
    b: str
    length_m: float
    diameter_mm: float
    open: bool = True
    condition: float = 1.0


def adjacency(mains: list[Main], excluded: set[str] = frozenset()) -> dict[str, list[tuple[str, Main]]]:
    graph = defaultdict(list)
    for main in mains:
        if not main.open or main.main_id in excluded:
            continue
        graph[main.a].append((main.b, main))
        graph[main.b].append((main.a, main))
    return dict(graph)


def reachable_from_sources(nodes: list[Junction], mains: list[Main], excluded: set[str] = frozenset()) -> set[str]:
    graph = adjacency(mains, excluded)
    sources = {n.node_id for n in nodes if n.source}
    seen = set(sources)
    queue = deque(sorted(sources))
    while queue:
        node = queue.popleft()
        for nxt, _ in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def unsupplied_demand(nodes: list[Junction], mains: list[Main], excluded: set[str]) -> float:
    supplied = reachable_from_sources(nodes, mains, excluded)
    return sum(n.demand_l_s for n in nodes if n.node_id not in supplied)


def unsupplied_critical(nodes: list[Junction], mains: list[Main], excluded: set[str]) -> list[str]:
    supplied = reachable_from_sources(nodes, mains, excluded)
    return sorted(n.node_id for n in nodes if n.critical and n.node_id not in supplied)


def hydraulic_weight(main: Main) -> float:
    if main.length_m <= 0 or main.diameter_mm <= 0 or not 0 < main.condition <= 1:
        raise ValueError('invalid main')
    diameter_m = main.diameter_mm / 1000.0
    return main.length_m / (diameter_m ** 4.87 * main.condition)


def shortest_hydraulic_path(source: str, target: str, mains: list[Main]) -> tuple[float, list[str]] | None:
    graph = adjacency(mains)
    heap = [(0.0, source, [])]
    best = {source: 0.0}
    while heap:
        cost, node, path = heappop(heap)
        if cost != best.get(node):
            continue
        if node == target:
            return cost, path
        for nxt, main in graph.get(node, []):
            new_cost = cost + hydraulic_weight(main)
            if new_cost < best.get(nxt, float('inf')):
                best[nxt] = new_cost
                heappush(heap, (new_cost, nxt, path + [main.main_id]))
    return None


def connected_components(nodes: list[Junction], mains: list[Main]) -> list[set[str]]:
    graph = adjacency(mains)
    all_nodes = {n.node_id for n in nodes}
    seen = set()
    result = []
    for start in sorted(all_nodes):
        if start in seen:
            continue
        component = {start}
        seen.add(start)
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            for nxt, _ in graph.get(cur, []):
                if nxt not in seen:
                    seen.add(nxt)
                    component.add(nxt)
                    queue.append(nxt)
        result.append(component)
    return result


def dead_end_nodes(nodes: list[Junction], mains: list[Main]) -> list[str]:
    graph = adjacency(mains)
    return sorted(n.node_id for n in nodes if len(graph.get(n.node_id, [])) <= 1 and not n.source)


def isolation_impact(main_id: str, nodes: list[Junction], mains: list[Main]) -> dict[str, object]:
    excluded = {main_id}
    supplied = reachable_from_sources(nodes, mains, excluded)
    impacted = [n for n in nodes if n.node_id not in supplied]
    return {
        'main_id': main_id,
        'junctions': len(impacted),
        'demand_l_s': sum(n.demand_l_s for n in impacted),
        'critical_nodes': sorted(n.node_id for n in impacted if n.critical),
    }


def rank_critical_mains(nodes: list[Junction], mains: list[Main]) -> list[dict[str, object]]:
    rows = [isolation_impact(m.main_id, nodes, mains) for m in mains if m.open]
    rows.sort(key=lambda r: (-len(r['critical_nodes']), -r['demand_l_s'], -r['junctions'], r['main_id']))
    return rows


def alternate_source_count(node_id: str, nodes: list[Junction], mains: list[Main]) -> int:
    sources = [n.node_id for n in nodes if n.source]
    return sum(1 for source in sources if shortest_hydraulic_path(source, node_id, mains) is not None)


def source_assignment(nodes: list[Junction], mains: list[Main]) -> dict[str, str | None]:
    sources = sorted(n.node_id for n in nodes if n.source)
    result = {}
    for node in nodes:
        if node.source:
            result[node.node_id] = node.node_id
            continue
        options = []
        for source in sources:
            route = shortest_hydraulic_path(source, node.node_id, mains)
            if route is not None:
                options.append((route[0], source))
        result[node.node_id] = min(options)[1] if options else None
    return result


def bfs_layers(source: str, mains: list[Main]) -> list[list[str]]:
    graph = adjacency(mains)
    seen = {source}
    frontier = [source]
    layers = []
    while frontier:
        layers.append(sorted(frontier))
        nxt = []
        for node in frontier:
            for other, _ in graph.get(node, []):
                if other not in seen:
                    seen.add(other)
                    nxt.append(other)
        frontier = nxt
    return layers


def loops(mains: list[Main]) -> list[tuple[str, str, str]]:
    graph = adjacency(mains)
    found = set()
    for a, edges in graph.items():
        neighbors = {b for b, _ in edges}
        for b in neighbors:
            common = neighbors & {c for c, _ in graph.get(b, [])}
            for c in common:
                tri = tuple(sorted((a, b, c)))
                if len(set(tri)) == 3:
                    found.add(tri)
    return sorted(found)


def validate_network(nodes: list[Junction], mains: list[Main]) -> list[str]:
    issues = []
    node_ids = {n.node_id for n in nodes}
    if len(node_ids) != len(nodes):
        issues.append('duplicate_node')
    main_ids = {m.main_id for m in mains}
    if len(main_ids) != len(mains):
        issues.append('duplicate_main')
    for main in mains:
        if main.a not in node_ids or main.b not in node_ids:
            issues.append(f'unknown_endpoint:{main.main_id}')
        if main.a == main.b:
            issues.append(f'self_loop:{main.main_id}')
        if main.length_m <= 0 or main.diameter_mm <= 0:
            issues.append(f'invalid_geometry:{main.main_id}')
    if not any(n.source for n in nodes):
        issues.append('no_source')
    return issues
