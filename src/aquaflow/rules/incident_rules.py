from dataclasses import dataclass
@dataclass(frozen=True)
class IncidentRule:
    asset:str
    severity:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:IncidentRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.severity<lo:return "low"
    if r.severity>hi:return "high"
    return "normal"
def margin(r:IncidentRule):
    if classify(r)!="normal":return 0.0
    return min(r.severity-(r.low+r.reserve),(r.high-r.reserve)-r.severity)
def normalized(r:IncidentRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.severity-(r.high+r.low)/2)/span)*1.00000000
def prioritize(rows:list[IncidentRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
