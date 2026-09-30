from dataclasses import dataclass
@dataclass(frozen=True)
class HydrantRule:
    asset:str
    velocity:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:HydrantRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.velocity<lo:return "low"
    if r.velocity>hi:return "high"
    return "normal"
def margin(r:HydrantRule):
    if classify(r)!="normal":return 0.0
    return min(r.velocity-(r.low+r.reserve),(r.high-r.reserve)-r.velocity)
def normalized(r:HydrantRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.velocity-(r.high+r.low)/2)/span)*0.88235294
def prioritize(rows:list[HydrantRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
