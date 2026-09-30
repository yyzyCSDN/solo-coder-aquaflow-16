from dataclasses import dataclass
@dataclass(frozen=True)
class Jar:
    raw_ntu:float; alkalinity:float; temp:float; dose:float; settled_ntu:float
def recommend(rows:list[Jar],ntu:float,alk:float,temp:float)->float:
    if not rows: raise ValueError("jar tests required")
    ranked=[]
    for r in rows:
        similarity=abs(r.raw_ntu-ntu)*.7+abs(r.alkalinity-alk)*.05+abs(r.temp-temp)*.2
        ranked.append((r.settled_ntu+similarity,r.dose))
    return min(ranked)[1]
