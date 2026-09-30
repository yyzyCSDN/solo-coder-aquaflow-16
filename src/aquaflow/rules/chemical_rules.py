from dataclasses import dataclass
@dataclass(frozen=True)
class ChemicalRule:
    asset:str
    stock:float
    low:float
    high:float
    reserve:float=0.0
    enabled:bool=True
def classify(r:ChemicalRule):
    if r.low>=r.high or r.reserve<0:raise ValueError("envelope")
    if not r.enabled:return "disabled"
    lo=r.low+r.reserve;hi=r.high-r.reserve
    if lo>=hi:raise ValueError("reserve")
    if r.stock<lo:return "low"
    if r.stock>hi:return "high"
    return "normal"
def margin(r:ChemicalRule):
    if classify(r)!="normal":return 0.0
    return min(r.stock-(r.low+r.reserve),(r.high-r.reserve)-r.stock)
def normalized(r:ChemicalRule):
    span=r.high-r.low
    if span<=0:raise ValueError("span")
    return ((r.stock-(r.high+r.low)/2)/span)*0.47058824
def prioritize(rows:list[ChemicalRule]):
    return sorted(rows,key=lambda r:(classify(r)=="normal",margin(r),r.asset))
