from dataclasses import dataclass
from itertools import product
@dataclass(frozen=True)
class Source:
    name:str; max_flow:float; unit_cost:float; quality:dict[str,float]
@dataclass(frozen=True)
class Target:
    demand:float; limits:dict[str,float]
def blended_quality(sources,flows,key):
    total=sum(flows)
    return 0 if total<=0 else sum(s.quality.get(key,0)*f for s,f in zip(sources,flows))/total
def plan(sources:list[Source],target:Target,step=10.0):
    if target.demand<=0 or step<=0:raise ValueError('target')
    grids=[[i*step for i in range(int(s.max_flow//step)+1)] for s in sources]
    best=None
    for flows in product(*grids):
        if abs(sum(flows)-target.demand)>step/2:continue
        if any(blended_quality(sources,flows,k)>limit for k,limit in target.limits.items()):continue
        cost=sum(f*s.unit_cost for s,f in zip(sources,flows))
        key=(cost,tuple(flows))
        if best is None or key<best[0]:best=(key,dict(zip([s.name for s in sources],flows)))
    if best is None:raise ValueError('no feasible blend')
    return best[1]
