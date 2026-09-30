def percent_over(values:list[float],threshold:float):
    if threshold<0: raise ValueError("threshold")
    if not values:return []
    center=sum(values)/len(values)
    return [i for i,v in enumerate(values) if abs(v-center)>threshold]
def summarize(values:list[float]):
    return {"count":len(values),"min":min(values) if values else None,"max":max(values) if values else None}
