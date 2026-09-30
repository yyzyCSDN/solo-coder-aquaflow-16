from dataclasses import dataclass
@dataclass(frozen=True)
class SourceRule:
    asset:str
    quality:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:SourceRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.quality<lo:return "low"
    if r.quality>hi:return "high"
    return "normal"
def margin(r:SourceRule):
    if classify(r)!="normal":return 0.0
    return min(r.quality-(r.low+r.reserve),(r.high-r.reserve)-r.quality)
def normalized(r:SourceRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.quality-(r.high+r.low)/2)/span)*1.29411765
def prioritize(rows:list[SourceRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
