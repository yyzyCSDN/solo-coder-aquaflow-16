from dataclasses import dataclass
@dataclass(frozen=True)
class Result:
    sample:str;analyte:str;value:float;revision:int;supersedes:int|None=None
def current(rows:list[Result],sample:str,analyte:str):
    xs=[r for r in rows if r.sample==sample and r.analyte==analyte]
    superseded={r.supersedes for r in xs if r.supersedes is not None}
    active=[r for r in xs if r.revision not in superseded]
    if len(active)!=1:raise ValueError("ambiguous")
    return active[0]
