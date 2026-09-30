from dataclasses import dataclass
@dataclass(frozen=True)
class CustomerRule:
    asset:str
    priority:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:CustomerRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.priority<lo:return "low"
    if r.priority>hi:return "high"
    return "normal"
def margin(r:CustomerRule):
    if classify(r)!="normal":return 0.0
    return min(r.priority-(r.low+r.reserve),(r.high-r.reserve)-r.priority)
def normalized(r:CustomerRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.priority-(r.high+r.low)/2)/span)*1.58823529
def prioritize(rows:list[CustomerRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
