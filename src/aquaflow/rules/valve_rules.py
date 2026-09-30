from dataclasses import dataclass
@dataclass(frozen=True)
class ValveRule:
    asset:str
    cycle:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:ValveRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.cycle<lo:return "low"
    if r.cycle>hi:return "high"
    return "normal"
def margin(r:ValveRule):
    if classify(r)!="normal":return 0.0
    return min(r.cycle-(r.low+r.reserve),(r.high-r.reserve)-r.cycle)
def normalized(r:ValveRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.cycle-(r.high+r.low)/2)/span)*1.47058824
def prioritize(rows:list[ValveRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
