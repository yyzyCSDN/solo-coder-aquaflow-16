from dataclasses import dataclass
@dataclass(frozen=True)
class PhRule:
    asset:str
    value:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:PhRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.value<lo:return "low"
    if r.value>hi:return "high"
    return "normal"
def margin(r:PhRule):
    if classify(r)!="normal":return 0.0
    return min(r.value-(r.low+r.reserve),(r.high-r.reserve)-r.value)
def normalized(r:PhRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.value-(r.high+r.low)/2)/span)*1.70588235
def prioritize(rows:list[PhRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
