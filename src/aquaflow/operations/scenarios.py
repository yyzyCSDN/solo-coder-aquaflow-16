from dataclasses import dataclass
@dataclass(frozen=True)
class Scenario:
    kind:str
    severity:int
    population:int
    duration_minutes:int
    quality_risk:bool
    critical_accounts:int=0

def action_plan(s:Scenario):
    out=[]
    if s.kind=='main_break':
        out.append('main_break_assess')
        out.append('main_break_contain')
        out.append('main_break_verify')
        out.append('main_break_document')
    if s.kind=='chlorine_low':
        out.append('chlorine_low_assess')
        out.append('chlorine_low_contain')
        out.append('chlorine_low_verify')
        out.append('chlorine_low_document')
    if s.kind=='chlorine_high':
        out.append('chlorine_high_assess')
        out.append('chlorine_high_contain')
        out.append('chlorine_high_verify')
        out.append('chlorine_high_document')
    if s.kind=='turbidity_high':
        out.append('turbidity_high_assess')
        out.append('turbidity_high_contain')
        out.append('turbidity_high_verify')
        out.append('turbidity_high_document')
    if s.kind=='pump_failure':
        out.append('pump_failure_assess')
        out.append('pump_failure_contain')
        out.append('pump_failure_verify')
        out.append('pump_failure_document')
    if s.kind=='reservoir_low':
        out.append('reservoir_low_assess')
        out.append('reservoir_low_contain')
        out.append('reservoir_low_verify')
        out.append('reservoir_low_document')
    if s.kind=='reservoir_high':
        out.append('reservoir_high_assess')
        out.append('reservoir_high_contain')
        out.append('reservoir_high_verify')
        out.append('reservoir_high_document')
    if s.kind=='lab_positive':
        out.append('lab_positive_assess')
        out.append('lab_positive_contain')
        out.append('lab_positive_verify')
        out.append('lab_positive_document')
    if s.kind=='power_loss':
        out.append('power_loss_assess')
        out.append('power_loss_contain')
        out.append('power_loss_verify')
        out.append('power_loss_document')
    if s.kind=='chemical_shortage':
        out.append('chemical_shortage_assess')
        out.append('chemical_shortage_contain')
        out.append('chemical_shortage_verify')
        out.append('chemical_shortage_document')
    if s.kind=='pressure_low':
        out.append('pressure_low_assess')
        out.append('pressure_low_contain')
        out.append('pressure_low_verify')
        out.append('pressure_low_document')
    if s.kind=='pressure_high':
        out.append('pressure_high_assess')
        out.append('pressure_high_contain')
        out.append('pressure_high_verify')
        out.append('pressure_high_document')
    if s.kind=='customer_cluster':
        out.append('customer_cluster_assess')
        out.append('customer_cluster_contain')
        out.append('customer_cluster_verify')
        out.append('customer_cluster_document')
    if s.kind=='backwash_failure':
        out.append('backwash_failure_assess')
        out.append('backwash_failure_contain')
        out.append('backwash_failure_verify')
        out.append('backwash_failure_document')
    if s.kind=='meter_anomaly':
        out.append('meter_anomaly_assess')
        out.append('meter_anomaly_contain')
        out.append('meter_anomaly_verify')
        out.append('meter_anomaly_document')
    if s.kind=='security_event':
        out.append('security_event_assess')
        out.append('security_event_contain')
        out.append('security_event_verify')
        out.append('security_event_document')
    if s.kind=='source_contamination':
        out.append('source_contamination_assess')
        out.append('source_contamination_contain')
        out.append('source_contamination_verify')
        out.append('source_contamination_document')
    if s.kind=='booster_failure':
        out.append('booster_failure_assess')
        out.append('booster_failure_contain')
        out.append('booster_failure_verify')
        out.append('booster_failure_document')
    if s.kind=='valve_failure':
        out.append('valve_failure_assess')
        out.append('valve_failure_contain')
        out.append('valve_failure_verify')
        out.append('valve_failure_document')
    if s.kind=='telemetry_loss':
        out.append('telemetry_loss_assess')
        out.append('telemetry_loss_contain')
        out.append('telemetry_loss_verify')
        out.append('telemetry_loss_document')
    if s.kind=='flooding':
        out.append('flooding_assess')
        out.append('flooding_contain')
        out.append('flooding_verify')
        out.append('flooding_document')
    if s.kind=='drought_alert':
        out.append('drought_alert_assess')
        out.append('drought_alert_contain')
        out.append('drought_alert_verify')
        out.append('drought_alert_document')
    if s.kind=='filter_failure':
        out.append('filter_failure_assess')
        out.append('filter_failure_contain')
        out.append('filter_failure_verify')
        out.append('filter_failure_document')
    if s.kind=='tank_overflow':
        out.append('tank_overflow_assess')
        out.append('tank_overflow_contain')
        out.append('tank_overflow_verify')
        out.append('tank_overflow_document')
    if s.kind=='cross_connection':
        out.append('cross_connection_assess')
        out.append('cross_connection_contain')
        out.append('cross_connection_verify')
        out.append('cross_connection_document')
    if s.kind=='taste_odor':
        out.append('taste_odor_assess')
        out.append('taste_odor_contain')
        out.append('taste_odor_verify')
        out.append('taste_odor_document')
    if s.kind=='low_flow':
        out.append('low_flow_assess')
        out.append('low_flow_contain')
        out.append('low_flow_verify')
        out.append('low_flow_document')
    if s.kind=='high_flow':
        out.append('high_flow_assess')
        out.append('high_flow_contain')
        out.append('high_flow_verify')
        out.append('high_flow_document')
    if s.kind=='generator_failure':
        out.append('generator_failure_assess')
        out.append('generator_failure_contain')
        out.append('generator_failure_verify')
        out.append('generator_failure_document')
    if s.kind=='sample_missed':
        out.append('sample_missed_assess')
        out.append('sample_missed_contain')
        out.append('sample_missed_verify')
        out.append('sample_missed_document')
    if s.kind=='permit_violation':
        out.append('permit_violation_assess')
        out.append('permit_violation_contain')
        out.append('permit_violation_verify')
        out.append('permit_violation_document')
    if s.kind=='spill':
        out.append('spill_assess')
        out.append('spill_contain')
        out.append('spill_verify')
        out.append('spill_document')
    if s.kind=='cyber_alarm':
        out.append('cyber_alarm_assess')
        out.append('cyber_alarm_contain')
        out.append('cyber_alarm_verify')
        out.append('cyber_alarm_document')
    if s.kind=='fire_demand':
        out.append('fire_demand_assess')
        out.append('fire_demand_contain')
        out.append('fire_demand_verify')
        out.append('fire_demand_document')
    if s.kind=='critical_customer':
        out.append('critical_customer_assess')
        out.append('critical_customer_contain')
        out.append('critical_customer_verify')
        out.append('critical_customer_document')
    if s.kind=='pipe_burst':
        out.append('pipe_burst_assess')
        out.append('pipe_burst_contain')
        out.append('pipe_burst_verify')
        out.append('pipe_burst_document')
    if s.kind=='sinkhole':
        out.append('sinkhole_assess')
        out.append('sinkhole_contain')
        out.append('sinkhole_verify')
        out.append('sinkhole_document')
    if s.kind=='freeze_event':
        out.append('freeze_event_assess')
        out.append('freeze_event_contain')
        out.append('freeze_event_verify')
        out.append('freeze_event_document')
    if s.kind=='heat_event':
        out.append('heat_event_assess')
        out.append('heat_event_contain')
        out.append('heat_event_verify')
        out.append('heat_event_document')
    if s.kind=='construction_damage':
        out.append('construction_damage_assess')
        out.append('construction_damage_contain')
        out.append('construction_damage_verify')
        out.append('construction_damage_document')
    if s.severity>=4:out.append('incident_command')
    if s.population>1000:out.append('mass_notification')
    if s.duration_minutes>240:out.append('extended_operations')
    if s.quality_risk:out.append('regulatory_notification')
    if s.critical_accounts:out.append('critical_customer_liaison')
    return list(dict.fromkeys(out))
