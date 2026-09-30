from dataclasses import dataclass
@dataclass(frozen=True)
class Customer:
    account:str;node:str;critical:bool;population:int
def summarize(rows:list[Customer],nodes:set[str]):
    hit=[r for r in rows if r.node in nodes]
    return {"accounts":len(hit),"population":sum(r.population for r in hit),"critical":sum(1 for r in hit if r.critical)}
