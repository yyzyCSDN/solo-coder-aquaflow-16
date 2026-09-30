from dataclasses import dataclass
@dataclass(frozen=True)
class DroughtRule:
    asset:str
    storage:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:DroughtRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.storage<lo:return "low"
    if r.storage>hi:return "high"
    return "normal"
def margin(r:DroughtRule):
    if classify(r)!="normal":return 0.0
    return min(r.storage-(r.low+r.reserve),(r.high-r.reserve)-r.storage)
def normalized(r:DroughtRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.storage-(r.high+r.low)/2)/span)*1.23529412
def prioritize(rows:list[DroughtRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
