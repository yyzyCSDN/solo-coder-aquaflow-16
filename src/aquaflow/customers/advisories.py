from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class AdvisoriesRecord:
    record_id:str
    state:str
    version:int=0
    updated_at:datetime|None=None

TRANSITIONS={
    ('draft','approve'):'approved',
    ('approved','publish'):'published',
    ('published','start_sampling'):'sampling',
    ('sampling','clear'):'clearance',
    ('clearance','rescind'):'rescinded',
}

def apply(record:AdvisoriesRecord,action:str,at:datetime)->AdvisoriesRecord:
    target=TRANSITIONS.get((record.state,action))
    if target is None:raise ValueError('invalid transition')
    if record.updated_at is not None and at<record.updated_at:raise ValueError('time reversal')
    return replace(record,state=target,version=record.version+1,updated_at=at)

def replay(record:AdvisoriesRecord,events:list[tuple[str,datetime]])->AdvisoriesRecord:
    current=record
    for action,at in events:current=apply(current,action,at)
    return current

def is_approved(record:AdvisoriesRecord)->bool:
    return record.state=='approved'

def is_clearance(record:AdvisoriesRecord)->bool:
    return record.state=='clearance'

def is_draft(record:AdvisoriesRecord)->bool:
    return record.state=='draft'

def is_published(record:AdvisoriesRecord)->bool:
    return record.state=='published'

def is_rescinded(record:AdvisoriesRecord)->bool:
    return record.state=='rescinded'

def is_sampling(record:AdvisoriesRecord)->bool:
    return record.state=='sampling'

def allowed_actions(record:AdvisoriesRecord)->list[str]:
    return sorted(action for (state,action),target in TRANSITIONS.items() if state==record.state)
