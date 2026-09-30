from dataclasses import dataclass
@dataclass(frozen=True)
class FilterRule:
    asset:str
    headloss:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:FilterRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.headloss<lo:return "low"
    if r.headloss>hi:return "high"
    return "normal"
def margin(r:FilterRule):
    if classify(r)!="normal":return 0.0
    return min(r.headloss-(r.low+r.reserve),(r.high-r.reserve)-r.headloss)
def normalized(r:FilterRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.headloss-(r.high+r.low)/2)/span)*0.41176471
def prioritize(rows:list[FilterRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
