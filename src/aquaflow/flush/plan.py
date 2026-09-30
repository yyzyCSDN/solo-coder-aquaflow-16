from dataclasses import dataclass
@dataclass(frozen=True)
class Hydrant:
    id:str;flow:float;sensitive:bool
def waves(rows:list[Hydrant],required:float,max_parallel:int):
    left=sorted(rows,key=lambda h:(h.sensitive,-h.flow,h.id));out=[]
    while left:
        wave=[];flow=0
        for h in list(left):
            if len(wave)>=max_parallel:break
            if h.sensitive and wave:continue
            wave.append(h.id);flow+=h.flow;left.remove(h)
            if flow>=required:break
        if flow<required:raise ValueError("insufficient")
        out.append(wave)
    return out
