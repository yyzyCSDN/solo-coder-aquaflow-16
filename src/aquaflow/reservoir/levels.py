from dataclasses import dataclass
@dataclass(frozen=True)
class Record:
    key:str;value:float;limit:float;enabled:bool=True
def alarm_state(rows:list[Record]):
    out={}
    for r in rows:
        if r.limit<0:raise ValueError("limit")
        if r.enabled:out[r.key]=r.value<=r.limit
    return out
def failures(rows:list[Record]):
    return sorted(k for k,v in alarm_state(rows).items() if not v)
