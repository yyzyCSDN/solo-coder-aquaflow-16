from dataclasses import dataclass
@dataclass(frozen=True)
class Input:
    a:float;b:float;c:float=0.0
def criticality(x:Input):
    if x.a<0 or x.b<=0: raise ValueError("invalid assets")
    return (x.a*x.b+x.c)/(1+x.b)
def evaluate_many(rows:list[Input]):
    return [criticality(r) for r in rows]
