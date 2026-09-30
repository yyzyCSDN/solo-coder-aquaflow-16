from dataclasses import dataclass
@dataclass(frozen=True)
class Revision:
    revision:int;sequence:int;open_pipes:frozenset[str]
def at(sequence:int,rows:list[Revision]):
    xs=[r for r in rows if r.sequence<=sequence]
    if not xs:raise ValueError("no revision")
    return max(xs,key=lambda r:(r.sequence,r.revision))
