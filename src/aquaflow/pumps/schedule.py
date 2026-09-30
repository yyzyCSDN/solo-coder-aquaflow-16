from dataclasses import dataclass
@dataclass(frozen=True)
class Pump:
    id:str;kw:float;flow:float;min_run:float;min_rest:float
@dataclass(frozen=True)
class Hist:
    running:bool;since_start:float;since_stop:float
def choose(pumps:list[Pump],hist:dict[str,Hist],required:float,max_kw:float):
    eligible=[]
    for p in pumps:
        h=hist[p.id]
        if not h.running and h.since_stop<p.min_rest:continue
        eligible.append(p)
    best=None
    for mask in range(1<<len(eligible)):
        rows=[eligible[i] for i in range(len(eligible)) if mask&(1<<i)]
        if sum(x.flow for x in rows)>=required and sum(x.kw for x in rows)<=max_kw:
            key=(sum(x.kw for x in rows),len(rows),tuple(sorted(x.id for x in rows)))
            if best is None or key<best[0]:best=(key,[x.id for x in rows])
    if best is None:raise ValueError("no feasible combination")
    return best[1]
