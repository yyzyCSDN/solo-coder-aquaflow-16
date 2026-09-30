from dataclasses import dataclass
from datetime import datetime
@dataclass(frozen=True)
class Filter:
    id:str; headloss:float; turbidity:float; last_backwash:datetime; online:bool=True
def choose(rows:list[Filter],now:datetime,max_offline:int,offline:set[str]):
    if len(offline)>=max_offline:return None
    ranked=[]
    for r in rows:
        if not r.online or r.id in offline:continue
        age=(now-r.last_backwash).total_seconds()/3600
        ranked.append((r.headloss*4+r.turbidity*8+age*.03,r.id))
    return max(ranked,default=(0,None))[1]
