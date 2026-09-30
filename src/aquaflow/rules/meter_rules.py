from dataclasses import dataclass
@dataclass(frozen=True)
class MeterRule:
    asset:str
    variance:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:MeterRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.variance<lo:return "low"
    if r.variance>hi:return "high"
    return "normal"
def margin(r:MeterRule):
    if classify(r)!="normal":return 0.0
    return min(r.variance-(r.low+r.reserve),(r.high-r.reserve)-r.variance)
def normalized(r:MeterRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.variance-(r.high+r.low)/2)/span)*0.52941176
def prioritize(rows:list[MeterRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
