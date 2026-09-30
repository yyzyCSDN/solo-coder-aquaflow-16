from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime

@dataclass(frozen=True)
class DeliveriesRecord:
    record_id:str
    state:str
    version:int=0
    updated_at:datetime|None=None

TRANSITIONS={
    ('planned','dispatch'):'enroute',
    ('enroute','arrive'):'arrived',
    ('arrived','sample'):'sampling',
    ('sampling','approve_unload'):'unloading',
    ('unloading','receive'):'received',
}

def apply(record:DeliveriesRecord,action:str,at:datetime)->DeliveriesRecord:
    target=TRANSITIONS.get((record.state,action))
    if target is None:raise ValueError('invalid transition')
    if record.updated_at is not None and at<record.updated_at:raise ValueError('time reversal')
    return replace(record,state=target,version=record.version+1,updated_at=at)

def replay(record:DeliveriesRecord,events:list[tuple[str,datetime]])->DeliveriesRecord:
    current=record
    for action,at in events:current=apply(current,action,at)
    return current

def is_arrived(record:DeliveriesRecord)->bool:
    return record.state=='arrived'

def is_enroute(record:DeliveriesRecord)->bool:
    return record.state=='enroute'

def is_planned(record:DeliveriesRecord)->bool:
    return record.state=='planned'

def is_received(record:DeliveriesRecord)->bool:
    return record.state=='received'

def is_sampling(record:DeliveriesRecord)->bool:
    return record.state=='sampling'

def is_unloading(record:DeliveriesRecord)->bool:
    return record.state=='unloading'

def allowed_actions(record:DeliveriesRecord)->list[str]:
    return sorted(action for (state,action),target in TRANSITIONS.items() if state==record.state)
