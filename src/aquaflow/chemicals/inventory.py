from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True)
class Lot:
    id:str;gross_kg:Decimal;concentration:Decimal;released:bool=True
def active_mass(rows:list[Lot]):
    total=Decimal(0)
    for r in rows:
        if r.gross_kg<0 or not 0<r.concentration<=1:raise ValueError("lot")
        if r.released:total+=r.gross_kg*r.concentration
    return total
