from dataclasses import dataclass
from datetime import datetime,timedelta
@dataclass(frozen=True)
class Reading:
    at:datetime;value:float
def average(rows:list[Reading],window:timedelta,at:datetime):
    start=at-window
    vals=[r.value for r in rows if start<r.at<=at]
    return None if not vals else sum(vals)/len(vals)
