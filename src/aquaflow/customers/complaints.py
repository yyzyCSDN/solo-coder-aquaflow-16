from dataclasses import dataclass
@dataclass(frozen=True)
class Record:
    key:str;value:float;limit:float;enabled:bool=True
def complaint_score(rows:list[Record]):
    out={}
    for r in rows:
        if r.limit<0:raise ValueError("limit")
        if r.enabled:out[r.key]=r.value<=r.limit
    return out
def failures(rows:list[Record]):
    return sorted(k for k,v in complaint_score(rows).items() if not v)
