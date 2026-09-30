from dataclasses import dataclass
from collections import defaultdict,deque
@dataclass(frozen=True)
class Pipe:
    id:str;a:str;b:str;open:bool=True
def isolated(nodes:set[str],pipes:list[Pipe],closed:set[str],sources:set[str])->set[str]:
    adj=defaultdict(set)
    for p in pipes:
        if p.open and p.id not in closed:
            adj[p.a].add(p.b);adj[p.b].add(p.a)
    seen=set(sources);q=deque(sources)
    while q:
        n=q.popleft()
        for x in adj[n]:
            if x not in seen:seen.add(x);q.append(x)
    return nodes-seen
