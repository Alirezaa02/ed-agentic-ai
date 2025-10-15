from typing import Dict, List
def vitals_flag(v: Dict) -> List[str]:
    flags = []
    if v.get("hr",0) > 100: flags.append("tachycardia")
    if v.get("rr",0) > 22:  flags.append("tachypnoea")
    if v.get("sbp",999) < 100: flags.append("low SBP")
    if v.get("temp",0) >= 38.0: flags.append("fever")
    if v.get("spo2",100) < 92:  flags.append("low SpO2")
    return flags
def make_summary(patient, visit, recent_visits):
    flags = vitals_flag({"hr": visit.hr, "rr": visit.rr, "sbp": visit.sbp, "temp": visit.temp, "spo2": visit.spo2})
    lines = [
        f"🧾 Patient: {patient.name} ({patient.age} {patient.sex})  | Allergies: {patient.allergies}",
        f"PMHx: {patient.pmhx}",
        f"Meds: {patient.meds}",
        f"Presenting: {visit.presenting} | Triage Cat: {visit.triage_cat} | Arrival: {visit.arrival_mode}",
        f"Vitals: HR {visit.hr}, RR {visit.rr}, SBP {visit.sbp}, Temp {visit.temp}, SpO2 {visit.spo2}",
    ]
    if flags:
        lines.append("⚠️ Abnormal: " + ", ".join(flags))
    if visit.ecg_flag: lines.append("ECG: abnormal flag present")
    if visit.lab_abn:  lines.append("Labs: abnormal results flagged")
    lines.append(f"Recent ED visits (30d): {visit.prev_ed_30d}")
    if recent_visits:
        lines.append("Last known visits: " + ", ".join(f"{rv.presenting} (Cat {rv.triage_cat})" for rv in recent_visits[:3]))
    lines.append("Suggestions: consider guideline-aligned orders based on presenting problem and flags (clinician to confirm).")
    return "\n".join(lines)
