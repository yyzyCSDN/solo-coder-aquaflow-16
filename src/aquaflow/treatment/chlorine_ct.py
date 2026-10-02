import math
from dataclasses import dataclass

REFERENCE_TEMPERATURE_C=20.0
# van't Hoff/Q10=2 chlorination kinetics: rate doubles per +10C, so CT credit
# relative to the 20C reference scales by 2**((T-20)/10); exactly 1.0 at 20C.
Q10_PER_10C=2.0

@dataclass(frozen=True)
class Segment:
    minutes:float; residual:float; baffling:float; temperature_c:float

def temperature_factor(temperature_c:float)->float:
    return Q10_PER_10C**((temperature_c-REFERENCE_TEMPERATURE_C)/10.0)

def effective_ct(rows:list[Segment])->float:
    total=0.0
    for r in rows:
        if r.minutes<=0 or r.residual<0 or not 0<r.baffling<=1 or not math.isfinite(r.temperature_c): raise ValueError("invalid")
        total+=r.minutes*r.residual*r.baffling*temperature_factor(r.temperature_c)
    return total

def compliant(rows,required): return required>0 and effective_ct(rows)>=required
