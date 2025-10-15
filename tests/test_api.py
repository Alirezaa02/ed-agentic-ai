import pytest
from httpx import AsyncClient
from app import app
@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get('/health'); assert r.status_code==200
@pytest.mark.asyncio
async def test_summary_predict_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get('/patient/P001/summary'); assert r.status_code==200
        payload={"patient_id":"P001","visit_id":None,"hr":102,"rr":22,"sbp":168,"temp":37.2,"spo2":96,"triage_cat":3,"ecg_flag":1,"lab_abn":1,"prev_ed_30d":0,"arrival_mode":"Walk-in"}
        r = await ac.post('/disposition/predict', json=payload); assert r.status_code==200
