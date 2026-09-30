from dataclasses import dataclass
@dataclass(frozen=True)
class Unit:
    id:str;healthy:bool;rank:int;capacity:float
def choose(rows:list[Unit],required:float,failed:str):
    rows=sorted([r for r in rows if r.healthy and r.id!=failed],key=lambda r:(r.rank,-r.capacity,r.id))
    out=[];cap=0
    for r in rows:
        out.append(r.id);cap+=r.capacity
        if cap>=required:return out
    raise ValueError("insufficient capacity")
