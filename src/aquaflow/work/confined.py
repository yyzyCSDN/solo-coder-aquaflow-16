from dataclasses import dataclass
from datetime import datetime
@dataclass(frozen=True)
class Permit:
    starts:datetime;ends:datetime;gas_test:datetime;attendant:str;entrant:str;rescue:str
def valid(p:Permit,at:datetime,max_age_min:int):
    if p.attendant==p.entrant or not p.rescue:return False
    if not p.starts<=at<p.ends:return False
    age=(at-p.gas_test).total_seconds()/60
    return 0<=age<=max_age_min
