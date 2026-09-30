from dataclasses import dataclass
from datetime import datetime,timedelta
@dataclass(frozen=True)
class Req:
    site:str;earliest:datetime;latest:datetime;minutes:int;certified:bool
@dataclass(frozen=True)
class Collector:
    name:str;certified:bool;start:datetime;end:datetime
def assign(reqs:list[Req],people:list[Collector]):
    busy={p.name:[] for p in people};out={}
    for r in sorted(reqs,key=lambda x:(x.latest,x.site)):
        opts=[]
        for p in people:
            if r.certified and not p.certified:continue
            s=max(r.earliest,p.start)
            while s+timedelta(minutes=r.minutes)<=min(r.latest,p.end):
                e=s+timedelta(minutes=r.minutes)
                if all(e<=a or s>=b for a,b in busy[p.name]):opts.append((s,p.name));break
                s+=timedelta(minutes=5)
        if not opts:raise ValueError("no collector")
        s,n=min(opts);out[r.site]=(n,s);busy[n].append((s,s+timedelta(minutes=r.minutes)))
    return out
