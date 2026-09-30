from dataclasses import dataclass
@dataclass(frozen=True)
class PumpOption:
    pump_id:str; flow:float; kw:float; available:bool; starts_remaining:int
@dataclass(frozen=True)
class Tariff:
    hour:int; price:float; demand_charge:float
def hourly_cost(pumps:list[PumpOption],tariff:Tariff)->float:
    kw=sum(p.kw for p in pumps)
    return kw*tariff.price+max(0,kw-100)*tariff.demand_charge
def dispatch(options:list[PumpOption],required:float,tariff:Tariff):
    eligible=[p for p in options if p.available and p.starts_remaining>0]
    best=None
    for mask in range(1<<len(eligible)):
        rows=[eligible[i] for i in range(len(eligible)) if mask&(1<<i)]
        if sum(p.flow for p in rows)<required:continue
        key=(hourly_cost(rows,tariff),sum(p.kw for p in rows),tuple(p.pump_id for p in rows))
        if best is None or key<best[0]:best=(key,[p.pump_id for p in rows])
    if best is None:raise ValueError('no dispatch')
    return best[1]
