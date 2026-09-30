from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class LimsCoreRecord:
    record_id:str
    state:str
    version:int=0
    updated_at:datetime|None=None

TRANSITIONS={
    ('received','accept'):'logged',
    ('logged','prepare'):'prepared',
    ('prepared','start_analysis'):'analyzing',
    ('analyzing','submit_result'):'review',
    ('review','release'):'released',
}

def apply(record:LimsCoreRecord,action:str,at:datetime)->LimsCoreRecord:
    target=TRANSITIONS.get((record.state,action))
    if target is None:raise ValueError('invalid transition')
    if record.updated_at is not None and at<record.updated_at:raise ValueError('time reversal')
    return replace(record,state=target,version=record.version+1,updated_at=at)

def replay(record:LimsCoreRecord,events:list[tuple[str,datetime]])->LimsCoreRecord:
    current=record
    for action,at in events:current=apply(current,action,at)
    return current

def is_analyzing(record:LimsCoreRecord)->bool:
    return record.state=='analyzing'

def is_logged(record:LimsCoreRecord)->bool:
    return record.state=='logged'

def is_prepared(record:LimsCoreRecord)->bool:
    return record.state=='prepared'

def is_received(record:LimsCoreRecord)->bool:
    return record.state=='received'

def is_released(record:LimsCoreRecord)->bool:
    return record.state=='released'

def is_review(record:LimsCoreRecord)->bool:
    return record.state=='review'

def allowed_actions(record:LimsCoreRecord)->list[str]:
    return sorted(action for (state,action),target in TRANSITIONS.items() if state==record.state)
