from collections import defaultdict
def holding_ok(pairs:list[tuple[str,float]]):
    grouped=defaultdict(list)
    for key,value in pairs:
        grouped[key].append(value)
    return {k:sum(v)/len(v) for k,v in grouped.items()}
def ordered(pairs:list[tuple[str,float]]):
    return sorted(holding_ok(pairs).items(),key=lambda x:(-x[1],x[0]))
