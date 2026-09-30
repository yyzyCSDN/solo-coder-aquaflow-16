from dataclasses import dataclass
@dataclass(frozen=True)
class BackflowRule:
    asset:str
    risk:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:BackflowRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.risk<lo:return "low"
    if r.risk>hi:return "high"
    return "normal"
def margin(r:BackflowRule):
    if classify(r)!="normal":return 0.0
    return min(r.risk-(r.low+r.reserve),(r.high-r.reserve)-r.risk)
def normalized(r:BackflowRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.risk-(r.high+r.low)/2)/span)*1.52941176
def prioritize(rows:list[BackflowRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
