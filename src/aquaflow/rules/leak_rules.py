from dataclasses import dataclass
@dataclass(frozen=True)
class LeakRule:
    asset:str
    signal:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:LeakRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.signal<lo:return "low"
    if r.signal>hi:return "high"
    return "normal"
def margin(r:LeakRule):
    if classify(r)!="normal":return 0.0
    return min(r.signal-(r.low+r.reserve),(r.high-r.reserve)-r.signal)
def normalized(r:LeakRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.signal-(r.high+r.low)/2)/span)*0.82352941
def prioritize(rows:list[LeakRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
