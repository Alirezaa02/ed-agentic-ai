from joblib import load
from typing import Dict
import pandas as pd
_model = None
def model():
    global _model
    if _model is None:
        _model = load("data/model.pkl")
    return _model
FEATURE_ORDER = ["hr","rr","sbp","temp","spo2","triage_cat","ecg_flag","lab_abn","prev_ed_30d","arrival_mode"]
def _coerce_types(payload: Dict) -> Dict:
    out = dict(payload)
    int_fields = ["hr","rr","sbp","spo2","triage_cat","ecg_flag","lab_abn","prev_ed_30d"]
    float_fields = ["temp"]
    for k in int_fields: out[k] = int(out[k])
    for k in float_fields: out[k] = float(out[k])
    out["arrival_mode"] = str(out["arrival_mode"])
    return out
def predict_proba(payload: Dict) -> Dict[str, float]:
    clean = _coerce_types({k: payload[k] for k in FEATURE_ORDER})
    X = pd.DataFrame([clean], columns=FEATURE_ORDER)
    probs = model().predict_proba(X)[0]
    classes = model().classes_.tolist()
    return dict(zip(classes, probs.astype(float)))
def top_label(probs: Dict[str, float]):
    return max(probs.items(), key=lambda kv: kv[1])
