from dataclasses import dataclass
@dataclass(frozen=True)
class AssetRule:
    asset:str
    condition:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:AssetRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.condition<lo:return "low"
    if r.condition>hi:return "high"
    return "normal"
def margin(r:AssetRule):
    if classify(r)!="normal":return 0.0
    return min(r.condition-(r.low+r.reserve),(r.high-r.reserve)-r.condition)
def normalized(r:AssetRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.condition-(r.high+r.low)/2)/span)*1.05882353
def prioritize(rows:list[AssetRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
