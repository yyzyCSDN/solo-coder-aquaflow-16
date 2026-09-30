from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class ResponseRecord:
    record_id:str
    state:str
    version:int=0
    updated_at:datetime|None=None

TRANSITIONS={
    ('detected','assess'):'assessed',
    ('assessed','isolate'):'isolated',
    ('isolated','dispatch_repair'):'repairing',
    ('repairing','restore'):'restoring',
    ('restoring','close'):'closed',
}

def apply(record:ResponseRecord,action:str,at:datetime)->ResponseRecord:
    target=TRANSITIONS.get((record.state,action))
    if target is None:raise ValueError('invalid transition')
    if record.updated_at is not None and at<record.updated_at:raise ValueError('time reversal')
    return replace(record,state=target,version=record.version+1,updated_at=at)

def replay(record:ResponseRecord,events:list[tuple[str,datetime]])->ResponseRecord:
    current=record
    for action,at in events:current=apply(current,action,at)
    return current

def is_assessed(record:ResponseRecord)->bool:
    return record.state=='assessed'

def is_closed(record:ResponseRecord)->bool:
    return record.state=='closed'

def is_detected(record:ResponseRecord)->bool:
    return record.state=='detected'

def is_isolated(record:ResponseRecord)->bool:
    return record.state=='isolated'

def is_repairing(record:ResponseRecord)->bool:
    return record.state=='repairing'

def is_restoring(record:ResponseRecord)->bool:
    return record.state=='restoring'

def allowed_actions(record:ResponseRecord)->list[str]:
    return sorted(action for (state,action),target in TRANSITIONS.items() if state==record.state)
