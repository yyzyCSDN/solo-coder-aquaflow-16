from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True)
class Meter:
    id:str;opening:Decimal;closing:Decimal;multiplier:Decimal
def volume(m:Meter):
    if m.closing<m.opening or m.multiplier<=0:raise ValueError("register")
    return (m.closing-m.opening)*m.multiplier
def balance(ins:list[Meter],outs:list[Meter],known_loss:Decimal):
    return sum((volume(x) for x in ins),Decimal(0))-sum((volume(x) for x in outs),Decimal(0))-known_loss
