from dataclasses import dataclass
from collections import defaultdict,deque
@dataclass(frozen=True)
class Node:
    id:str;demand:float;fixed_head:float|None=None
@dataclass(frozen=True)
class Link:
    id:str;a:str;b:str;resistance:float;enabled:bool=True
@dataclass(frozen=True)
class Result:
    heads:dict[str,float];flows:dict[str,float];converged:bool;iterations:int
def solve(nodes:list[Node],links:list[Link],iterations=200,tolerance=1e-5):
    nm={n.id:n for n in nodes}
    if len(nm)!=len(nodes):raise ValueError("duplicate node")
    adj=defaultdict(list)
    for l in links:
        if l.a not in nm or l.b not in nm or l.resistance<=0:raise ValueError("link")
        if l.enabled:adj[l.a].append(l);adj[l.b].append(l)
    roots=[n.id for n in nodes if n.fixed_head is not None]
    seen=set(roots);q=deque(roots)
    while q:
        x=q.popleft()
        for l in adj[x]:
            y=l.b if l.a==x else l.a
            if y not in seen:seen.add(y);q.append(y)
    if seen!=set(nm):raise ValueError("unsupplied component")
    heads={n.id:(n.fixed_head if n.fixed_head is not None else 30.0) for n in nodes}
    flows={l.id:0.0 for l in links}
    for it in range(1,iterations+1):
        change=0
        for n in nodes:
            if n.fixed_head is not None:continue
            numerator=denominator=0.0
            for l in adj[n.id]:
                other=l.b if l.a==n.id else l.a
                conductance=1/l.resistance
                numerator+=heads[other]*conductance;denominator+=conductance
            target=numerator/denominator-n.demand*.02
            new=heads[n.id]*.6+target*.4
            change=max(change,abs(new-heads[n.id]));heads[n.id]=new
        for l in links:
            flows[l.id]=0 if not l.enabled else (heads[l.a]-heads[l.b])/l.resistance
        if change<tolerance:return Result(heads,flows,True,it)
    return Result(heads,flows,False,iterations)
