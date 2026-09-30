from dataclasses import dataclass
@dataclass(frozen=True)
class DemandRule:
    asset:str
    flow:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:DemandRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.flow<lo:return "low"
    if r.flow>hi:return "high"
    return "normal"
def margin(r:DemandRule):
    if classify(r)!="normal":return 0.0
    return min(r.flow-(r.low+r.reserve),(r.high-r.reserve)-r.flow)
def normalized(r:DemandRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.flow-(r.high+r.low)/2)/span)*1.17647059
def prioritize(rows:list[DemandRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
