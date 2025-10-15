import pandas as pd
import asyncio
from models import Base, engine, SessionLocal, Patient, Visit
async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    patients = pd.read_csv("data/patients.csv")
    visits = pd.read_csv("data/visits.csv", parse_dates=["ts"])
    async with SessionLocal() as s:
        for _, r in patients.iterrows(): s.add(Patient(**r.to_dict()))
        for _, r in visits.iterrows():
            d = r.to_dict()
            if isinstance(d["ts"], pd.Timestamp): d["ts"] = d["ts"].to_pydatetime()
            s.add(Visit(**d))
        await s.commit()
if __name__ == "__main__":
    asyncio.run(main())
