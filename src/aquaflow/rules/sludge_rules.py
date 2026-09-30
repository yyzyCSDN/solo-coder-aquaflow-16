from dataclasses import dataclass
@dataclass(frozen=True)
class SludgeRule:
    asset:str
    solids:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:SludgeRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.solids<lo:return "low"
    if r.solids>hi:return "high"
    return "normal"
def margin(r:SludgeRule):
    if classify(r)!="normal":return 0.0
    return min(r.solids-(r.low+r.reserve),(r.high-r.reserve)-r.solids)
def normalized(r:SludgeRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.solids-(r.high+r.low)/2)/span)*1.35294118
def prioritize(rows:list[SludgeRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
