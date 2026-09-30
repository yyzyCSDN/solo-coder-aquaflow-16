from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class CasesRecord:
    record_id:str
    state:str
    version:int=0
    updated_at:datetime|None=None

TRANSITIONS={
    ('open','investigate'):'investigating',
    ('investigating','freeze_evidence'):'evidence_ready',
    ('evidence_ready','report'):'reported',
    ('reported','follow_up'):'followup',
    ('followup','close'):'closed',
}

def apply(record:CasesRecord,action:str,at:datetime)->CasesRecord:
    target=TRANSITIONS.get((record.state,action))
    if target is None:raise ValueError('invalid transition')
    if record.updated_at is not None and at<record.updated_at:raise ValueError('time reversal')
    return replace(record,state=target,version=record.version+1,updated_at=at)

def replay(record:CasesRecord,events:list[tuple[str,datetime]])->CasesRecord:
    current=record
    for action,at in events:current=apply(current,action,at)
    return current

def is_closed(record:CasesRecord)->bool:
    return record.state=='closed'

def is_evidence_ready(record:CasesRecord)->bool:
    return record.state=='evidence_ready'

def is_followup(record:CasesRecord)->bool:
    return record.state=='followup'

def is_investigating(record:CasesRecord)->bool:
    return record.state=='investigating'

def is_open(record:CasesRecord)->bool:
    return record.state=='open'

def is_reported(record:CasesRecord)->bool:
    return record.state=='reported'

def allowed_actions(record:CasesRecord)->list[str]:
    return sorted(action for (state,action),target in TRANSITIONS.items() if state==record.state)
