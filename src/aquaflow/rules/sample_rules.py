from dataclasses import dataclass
@dataclass(frozen=True)
class SampleRule:
    asset:str
    age:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:SampleRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.age<lo:return "low"
    if r.age>hi:return "high"
    return "normal"
def margin(r:SampleRule):
    if classify(r)!="normal":return 0.0
    return min(r.age-(r.low+r.reserve),(r.high-r.reserve)-r.age)
def normalized(r:SampleRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.age-(r.high+r.low)/2)/span)*0.70588235
def prioritize(rows:list[SampleRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
