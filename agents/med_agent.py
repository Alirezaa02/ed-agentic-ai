from typing import List, Dict
INTERACTIONS = {("Apixaban","NSAID"): "↑ bleeding risk; avoid or monitor closely"}
def check_allergy(meds: List[str], allergies: List[str]) -> List[str]:
    meds_lower=set(m.lower() for m in meds)
    alls_lower=set(a.lower() for a in allergies)
    return [m for m in meds if m.lower() in alls_lower]
def check_interactions(meds: List[str]) -> Dict[str,str]:
    results={}; meds_set=set(meds)
    for (a,b),note in INTERACTIONS.items():
        if a in meds_set and b in meds_set:
            results[f"{a}+{b}"]=note
    return results
def med_check(meds: List[str], allergies: List[str]) -> Dict:
    unsafe_allergy = check_allergy(meds, allergies)
    interactions = check_interactions(meds)
    verdict = "safe"; reasons=[]
    if unsafe_allergy:
        verdict="unsafe"; reasons += [f"Allergy conflict: {', '.join(unsafe_allergy)}"]
    if interactions:
        verdict="caution" if verdict=="safe" else verdict
        for k,v in interactions.items(): reasons.append(f"Interaction {k}: {v}")
    return {"verdict": verdict, "reasons": reasons}
