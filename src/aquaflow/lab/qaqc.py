from dataclasses import dataclass
@dataclass(frozen=True)
class Input:
    a:float;b:float;c:float=0.0
def rpd(x:Input):
    if x.a<0 or x.b<=0: raise ValueError("invalid qaqc")
    return (x.a*x.b+x.c)/(1+x.b)
def evaluate_many(rows:list[Input]):
    return [rpd(r) for r in rows]
