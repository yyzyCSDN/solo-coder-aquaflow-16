from dataclasses import dataclass
@dataclass(frozen=True)
class PowerRule:
    asset:str
    kw:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:PowerRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.kw<lo:return "low"
    if r.kw>hi:return "high"
    return "normal"
def margin(r:PowerRule):
    if classify(r)!="normal":return 0.0
    return min(r.kw-(r.low+r.reserve),(r.high-r.reserve)-r.kw)
def normalized(r:PowerRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.kw-(r.high+r.low)/2)/span)*1.41176471
def prioritize(rows:list[PowerRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
