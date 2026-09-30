from dataclasses import dataclass
@dataclass(frozen=True)
class BoosterRule:
    asset:str
    capacity:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:BoosterRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.capacity<lo:return "low"
    if r.capacity>hi:return "high"
    return "normal"
def margin(r:BoosterRule):
    if classify(r)!="normal":return 0.0
    return min(r.capacity-(r.low+r.reserve),(r.high-r.reserve)-r.capacity)
def normalized(r:BoosterRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.capacity-(r.high+r.low)/2)/span)*0.64705882
def prioritize(rows:list[BoosterRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
