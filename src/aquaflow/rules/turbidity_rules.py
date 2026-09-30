from dataclasses import dataclass
@dataclass(frozen=True)
class TurbidityRule:
    asset:str
    ntu:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:TurbidityRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.ntu<lo:return "low"
    if r.ntu>hi:return "high"
    return "normal"
def margin(r:TurbidityRule):
    if classify(r)!="normal":return 0.0
    return min(r.ntu-(r.low+r.reserve),(r.high-r.reserve)-r.ntu)
def normalized(r:TurbidityRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.ntu-(r.high+r.low)/2)/span)*1.64705882
def prioritize(rows:list[TurbidityRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
