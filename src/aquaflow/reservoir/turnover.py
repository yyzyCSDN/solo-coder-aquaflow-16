from dataclasses import dataclass
@dataclass(frozen=True)
class State:
    volume:float; inflow:float; outflow:float; age_hours:float
def project_age(s:State,hours:float)->float:
    if min(s.volume,s.inflow,s.outflow,hours)<0: raise ValueError("negative")
    if s.volume==0:return 0
    renewal=min(1,(s.inflow*hours)/s.volume)
    return (s.age_hours+hours)*(1-renewal)+(hours*.5)*renewal
