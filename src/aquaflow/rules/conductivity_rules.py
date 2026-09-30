from dataclasses import dataclass
@dataclass(frozen=True)
class ConductivityRule:
    asset:str
    us_cm:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:ConductivityRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.us_cm<lo:return "low"
    if r.us_cm>hi:return "high"
    return "normal"
def margin(r:ConductivityRule):
    if classify(r)!="normal":return 0.0
    return min(r.us_cm-(r.low+r.reserve),(r.high-r.reserve)-r.us_cm)
def normalized(r:ConductivityRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.us_cm-(r.high+r.low)/2)/span)*1.82352941
def prioritize(rows:list[ConductivityRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
