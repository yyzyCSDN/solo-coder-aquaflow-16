from dataclasses import dataclass
@dataclass(frozen=True)
class PressureRule:
    asset:str
    kpa:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:PressureRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.kpa<lo:return "low"
    if r.kpa>hi:return "high"
    return "normal"
def margin(r:PressureRule):
    if classify(r)!="normal":return 0.0
    return min(r.kpa-(r.low+r.reserve),(r.high-r.reserve)-r.kpa)
def normalized(r:PressureRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.kpa-(r.high+r.low)/2)/span)*0.29411765
def prioritize(rows:list[PressureRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
