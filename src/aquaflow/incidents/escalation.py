from dataclasses import dataclass
from datetime import datetime
@dataclass(frozen=True)
class Incident:
    severity:int;opened:datetime;ack:datetime|None
@dataclass(frozen=True)
class Rule:
    severity:int;minutes:int;role:str
def overdue(i:Incident,rules:list[Rule],now:datetime):
    if i.ack is not None:return set()
    elapsed=(now-i.opened).total_seconds()/60
    return {r.role for r in rules if i.severity>=r.severity and elapsed>r.minutes}
