from dataclasses import dataclass
@dataclass(frozen=True)
class ReservoirRule:
    asset:str
    level:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:ReservoirRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.level<lo:return "low"
    if r.level>hi:return "high"
    return "normal"
def margin(r:ReservoirRule):
    if classify(r)!="normal":return 0.0
    return min(r.level-(r.low+r.reserve),(r.high-r.reserve)-r.level)
def normalized(r:ReservoirRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.level-(r.high+r.low)/2)/span)*0.35294118
def prioritize(rows:list[ReservoirRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
