from dataclasses import dataclass
@dataclass(frozen=True)
class SpareRule:
    asset:str
    stock:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:SpareRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.stock<lo:return "low"
    if r.stock>hi:return "high"
    return "normal"
def margin(r:SpareRule):
    if classify(r)!="normal":return 0.0
    return min(r.stock-(r.low+r.reserve),(r.high-r.reserve)-r.stock)
def normalized(r:SpareRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.stock-(r.high+r.low)/2)/span)*1.11764706
def prioritize(rows:list[SpareRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
