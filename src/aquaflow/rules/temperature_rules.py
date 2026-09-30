from dataclasses import dataclass
@dataclass(frozen=True)
class TemperatureRule:
    asset:str
    celsius:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:TemperatureRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.celsius<lo:return "low"
    if r.celsius>hi:return "high"
    return "normal"
def margin(r:TemperatureRule):
    if classify(r)!="normal":return 0.0
    return min(r.celsius-(r.low+r.reserve),(r.high-r.reserve)-r.celsius)
def normalized(r:TemperatureRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.celsius-(r.high+r.low)/2)/span)*1.76470588
def prioritize(rows:list[TemperatureRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
