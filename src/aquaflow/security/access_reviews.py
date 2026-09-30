from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class AccessReviewsRecord:
    record_id:str
    state:str
    version:int=0
    updated_at:datetime|None=None

TRANSITIONS={
    ('open','collect'):'collected',
    ('collected','review'):'reviewed',
    ('reviewed','remediate'):'remediation',
    ('remediation','verify'):'verified',
    ('verified','close'):'closed',
}

def apply(record:AccessReviewsRecord,action:str,at:datetime)->AccessReviewsRecord:
    target=TRANSITIONS.get((record.state,action))
    if target is None:raise ValueError('invalid transition')
    if record.updated_at is not None and at<record.updated_at:raise ValueError('time reversal')
    return replace(record,state=target,version=record.version+1,updated_at=at)

def replay(record:AccessReviewsRecord,events:list[tuple[str,datetime]])->AccessReviewsRecord:
    current=record
    for action,at in events:current=apply(current,action,at)
    return current

def is_closed(record:AccessReviewsRecord)->bool:
    return record.state=='closed'

def is_collected(record:AccessReviewsRecord)->bool:
    return record.state=='collected'

def is_open(record:AccessReviewsRecord)->bool:
    return record.state=='open'

def is_remediation(record:AccessReviewsRecord)->bool:
    return record.state=='remediation'

def is_reviewed(record:AccessReviewsRecord)->bool:
    return record.state=='reviewed'

def is_verified(record:AccessReviewsRecord)->bool:
    return record.state=='verified'

def allowed_actions(record:AccessReviewsRecord)->list[str]:
    return sorted(action for (state,action),target in TRANSITIONS.items() if state==record.state)
