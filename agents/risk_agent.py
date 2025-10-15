from typing import Dict, List
def risk_assess(vitals: Dict) -> Dict:
    rr = int(vitals.get("rr", 0))
    sbp = int(vitals.get("sbp", 999))
    spo2 = int(vitals.get("spo2", 100))
    factors: List[str] = []
    if rr >= 22: factors.append("Tachypnoea (RR>=22)")
    if sbp <= 100: factors.append("Low SBP (<=100)")
    if spo2 < 92: factors.append("Hypoxaemia (SpO2<92)")
    if len(factors) >= 2: level = "high"
    elif len(factors) == 1: level = "medium"
    else: level = "low"
    return {"risk": level, "factors": factors}
