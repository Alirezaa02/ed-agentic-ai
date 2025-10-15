from __future__ import annotations
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import select, desc
from models import SessionLocal, Patient, Visit
from ai.summariser import make_summary
from ai.disposition import predict_proba, top_label
from agents.risk_agent import risk_assess
from agents.med_agent import med_check
import logging, uuid, time, os, json, hashlib
from datetime import datetime

app = FastAPI(title="ED Agentic AI", version="2.0.0", description="Charts, Calendar, Risk & Med Agents")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logger = logging.getLogger("ed-agentic-ai"); logging.basicConfig(level=logging.INFO)
def phash(s:str)->str: return hashlib.sha256(s.encode()).hexdigest()[:12]
def audit(event:str, payload:dict):
    rec={"ts": datetime.utcnow().isoformat()+"Z","event":event,**payload}
    os.makedirs("data", exist_ok=True)
    with open("data/audit.log","a") as f: f.write(json.dumps(rec)+"\n")
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id", str(uuid.uuid4())); start=time.time()
    try: response = await call_next(request)
    finally:
        dur = round((time.time()-start)*1000,1); logger.info({"evt":"http","rid":rid,"path":str(request.url.path),"ms":dur})
    response.headers["x-request-id"]=rid; return response

class PredictInput(BaseModel):
    patient_id: str
    visit_id: Optional[str] = None
    hr: int = Field(ge=20, le=220)
    rr: int = Field(ge=6, le=50)
    sbp: int = Field(ge=60, le=240)
    temp: float = Field(ge=30, le=43)
    spo2: int = Field(ge=50, le=100)
    triage_cat: int = Field(ge=1, le=5)
    ecg_flag: int = Field(ge=0, le=1)
    lab_abn: int = Field(ge=0, le=1)
    prev_ed_30d: int = Field(ge=0, le=10)
    arrival_mode: str

class MedCheckInput(BaseModel):
    meds: List[str]
    allergies: List[str] = []

@app.get("/", response_class=HTMLResponse, tags=["ui"])
async def home(request: Request):
    demo_ids=["P001","P002","P003"]; return templates.TemplateResponse("index.html", {"request":request,"demo_ids":demo_ids})

@app.get("/health", tags=["meta"])
def health(): return {"status":"ok"}

@app.get("/patient/{patient_id}/summary", tags=["history"])
async def patient_summary(patient_id: str):
    async with SessionLocal() as s:
        p = await s.get(Patient, patient_id)
        if not p: raise HTTPException(404,"Patient not found")
        q = select(Visit).where(Visit.patient_id==patient_id).order_by(desc(Visit.ts))
        v = (await s.execute(q)).scalars().first()
        if not v: raise HTTPException(404,"No visits found for patient")
        recent=(await s.execute(q.limit(4))).scalars().all()[1:]
        summary = make_summary(p, v, recent)
        return {"patient_id":patient_id,"visit_id":v.visit_id,"summary":summary}

@app.get("/patient/{patient_id}/vitals", tags=["charts"])
async def patient_vitals(patient_id: str):
    async with SessionLocal() as s:
        q = select(Visit).where(Visit.patient_id==patient_id).order_by(desc(Visit.ts))
        vs=(await s.execute(q)).scalars().all()
        if not vs: return []
        vs=list(reversed(vs))[-10:]
        return [{"ts":v.ts.isoformat(timespec="minutes"),"hr":v.hr,"rr":v.rr,"sbp":v.sbp} for v in vs]

@app.post("/disposition/predict", tags=["prediction"])
async def disposition_predict(inp: PredictInput):
    probs = predict_proba(inp.model_dump()); label, p = top_label(probs)
    rationale=[]; 
    if inp.triage_cat<=2: rationale.append("High-acuity triage")
    if inp.ecg_flag: rationale.append("Abnormal ECG")
    if inp.lab_abn: rationale.append("Abnormal labs")
    if inp.sbp<100 or inp.spo2<92: rationale.append("Unstable vital(s)")
    if inp.prev_ed_30d>0: rationale.append("Recent ED reattendance")
    if not rationale: rationale.append("Stable vitals, low-risk features")
    disposition={"prediction":label,"confidence":round(p,3),"probabilities":{k:round(v,3) for k,v in probs.items()},"rationale":rationale}
    if p<0.55: disposition["note"]="Low-confidence — clinician review required."
    audit("predict", {"patient":phash(inp.patient_id),"prediction":label,"confidence":round(p,3)})
    return disposition

@app.get("/agent/risk/{patient_id}", tags=["risk"])
async def risk_agent(patient_id: str):
    async with SessionLocal() as s:
        q = select(Visit).where(Visit.patient_id==patient_id).order_by(desc(Visit.ts))
        v = (await s.execute(q)).scalars().first()
        if not v: raise HTTPException(404,"No visits")
        result = risk_assess({"rr":v.rr,"sbp":v.sbp,"spo2":v.spo2})
        audit("risk_eval", {"patient":phash(patient_id), **result}); return result

@app.post("/medcheck", tags=["meds"])
def medcheck(inp: MedCheckInput):
    res = med_check(inp.meds, inp.allergies); audit("med_check", {"verdict":res["verdict"]}); return res

@app.get("/timeline/{patient_id}", tags=["timeline"])
async def timeline(patient_id: str):
    async with SessionLocal() as s:
        q = select(Visit).where(Visit.patient_id==patient_id).order_by(desc(Visit.ts))
        visits=(await s.execute(q)).scalars().all(); out=[]
        for v in reversed(visits):
            payload={"hr":v.hr,"rr":v.rr,"sbp":v.sbp,"temp":v.temp,"spo2":v.spo2,"triage_cat":v.triage_cat,"ecg_flag":v.ecg_flag,"lab_abn":v.lab_abn,"prev_ed_30d":v.prev_ed_30d,"arrival_mode":v.arrival_mode}
            probs = predict_proba(payload); label, conf = top_label(probs)
            out.append({"ts":v.ts.isoformat(timespec="minutes"),"visit_id":v.visit_id,"presenting":v.presenting,"prediction":label,"confidence":round(conf,3)})
        return out

@app.get("/calendar", tags=["calendar"])
async def calendar_feed():
    today = datetime.utcnow().date().isoformat()
    return [
        {"title":"Triage Briefing","start": f"{today}T08:30:00"},
        {"title":"Review P001","start": f"{today}T10:30:00","end": f"{today}T10:45:00"},
        {"title":"Short-stay Rounds","start": f"{today}T13:00:00"},
        {"title":"Bed Meeting","start": f"{today}T15:30:00"}
    ]
