from dataclasses import dataclass
@dataclass(frozen=True)
class Node:
    id:str;elevation_m:float;pressure_kpa:float
def classify(rows:list[Node],low:float,high:float):
    out={"low":[],"high":[]}
    for r in rows:
        corrected=r.pressure_kpa+r.elevation_m*9.80665/10
        if corrected<low:out["low"].append(r.id)
        elif corrected>high:out["high"].append(r.id)
    return out
