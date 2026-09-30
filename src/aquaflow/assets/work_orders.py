from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class WorkOrdersRecord:
    record_id:str
    state:str
    version:int=0
    updated_at:datetime|None=None

TRANSITIONS={
    ('draft','approve'):'approved',
    ('approved','schedule'):'scheduled',
    ('scheduled','start'):'in_progress',
    ('in_progress','complete_work'):'verification',
    ('verification','verify'):'closed',
}

def apply(record:WorkOrdersRecord,action:str,at:datetime)->WorkOrdersRecord:
    target=TRANSITIONS.get((record.state,action))
    if target is None:raise ValueError('invalid transition')
    if record.updated_at is not None and at<record.updated_at:raise ValueError('time reversal')
    return replace(record,state=target,version=record.version+1,updated_at=at)

def replay(record:WorkOrdersRecord,events:list[tuple[str,datetime]])->WorkOrdersRecord:
    current=record
    for action,at in events:current=apply(current,action,at)
    return current

def is_approved(record:WorkOrdersRecord)->bool:
    return record.state=='approved'

def is_closed(record:WorkOrdersRecord)->bool:
    return record.state=='closed'

def is_draft(record:WorkOrdersRecord)->bool:
    return record.state=='draft'

def is_in_progress(record:WorkOrdersRecord)->bool:
    return record.state=='in_progress'

def is_scheduled(record:WorkOrdersRecord)->bool:
    return record.state=='scheduled'

def is_verification(record:WorkOrdersRecord)->bool:
    return record.state=='verification'

def allowed_actions(record:WorkOrdersRecord)->list[str]:
    return sorted(action for (state,action),target in TRANSITIONS.items() if state==record.state)
