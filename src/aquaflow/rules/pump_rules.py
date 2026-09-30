from dataclasses import dataclass
@dataclass(frozen=True)
class PumpRule:
    asset:str
    load:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:PumpRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.load<lo:return "low"
    if r.load>hi:return "high"
    return "normal"
def margin(r:PumpRule):
    if classify(r)!="normal":return 0.0
    return min(r.load-(r.low+r.reserve),(r.high-r.reserve)-r.load)
def normalized(r:PumpRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.load-(r.high+r.low)/2)/span)*0.58823529
def prioritize(rows:list[PumpRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
