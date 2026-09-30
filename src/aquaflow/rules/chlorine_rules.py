from dataclasses import dataclass
@dataclass(frozen=True)
class ChlorineRule:
    asset:str
    residual:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:ChlorineRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.residual<lo:return "low"
    if r.residual>hi:return "high"
    return "normal"
def margin(r:ChlorineRule):
    if classify(r)!="normal":return 0.0
    return min(r.residual-(r.low+r.reserve),(r.high-r.reserve)-r.residual)
def normalized(r:ChlorineRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.residual-(r.high+r.low)/2)/span)*0.23529412
def prioritize(rows:list[ChlorineRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
