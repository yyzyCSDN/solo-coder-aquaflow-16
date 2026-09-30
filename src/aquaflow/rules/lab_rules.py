from dataclasses import dataclass
@dataclass(frozen=True)
class LabRule:
    asset:str
    qc:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:LabRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.qc<lo:return "low"
    if r.qc>hi:return "high"
    return "normal"
def margin(r:LabRule):
    if classify(r)!="normal":return 0.0
    return min(r.qc-(r.low+r.reserve),(r.high-r.reserve)-r.qc)
def normalized(r:LabRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.qc-(r.high+r.low)/2)/span)*0.76470588
def prioritize(rows:list[LabRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
