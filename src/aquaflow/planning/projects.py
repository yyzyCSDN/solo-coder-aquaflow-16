from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class ProjectsRecord:
    record_id:str
    state:str
    version:int=0
    updated_at:datetime|None=None

TRANSITIONS={
    ('candidate','screen'):'screened',
    ('screened','design'):'designed',
    ('designed','fund'):'funded',
    ('funded','construct'):'construction',
    ('construction','commission'):'commissioned',
}

def apply(record:ProjectsRecord,action:str,at:datetime)->ProjectsRecord:
    target=TRANSITIONS.get((record.state,action))
    if target is None:raise ValueError('invalid transition')
    if record.updated_at is not None and at<record.updated_at:raise ValueError('time reversal')
    return replace(record,state=target,version=record.version+1,updated_at=at)

def replay(record:ProjectsRecord,events:list[tuple[str,datetime]])->ProjectsRecord:
    current=record
    for action,at in events:current=apply(current,action,at)
    return current

def is_candidate(record:ProjectsRecord)->bool:
    return record.state=='candidate'

def is_commissioned(record:ProjectsRecord)->bool:
    return record.state=='commissioned'

def is_construction(record:ProjectsRecord)->bool:
    return record.state=='construction'

def is_designed(record:ProjectsRecord)->bool:
    return record.state=='designed'

def is_funded(record:ProjectsRecord)->bool:
    return record.state=='funded'

def is_screened(record:ProjectsRecord)->bool:
    return record.state=='screened'

def allowed_actions(record:ProjectsRecord)->list[str]:
    return sorted(action for (state,action),target in TRANSITIONS.items() if state==record.state)
