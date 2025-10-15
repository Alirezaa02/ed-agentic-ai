from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime
from datetime import datetime

DB_URL = "sqlite+aiosqlite:///./ed.db"
engine = create_async_engine(DB_URL, future=True, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase): pass

class Patient(Base):
    __tablename__ = "patients"
    patient_id: Mapped[str] = mapped_column(String, primary_key=True)
    nhs_no: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    age: Mapped[int]  = mapped_column(Integer)
    sex: Mapped[str]  = mapped_column(String)
    allergies: Mapped[str] = mapped_column(String)
    pmhx: Mapped[str] = mapped_column(String)
    meds: Mapped[str] = mapped_column(String)

class Visit(Base):
    __tablename__ = "visits"
    visit_id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(String, index=True)
    ts: Mapped[datetime] = mapped_column(DateTime)
    triage_cat: Mapped[int] = mapped_column(Integer)
    arrival_mode: Mapped[str] = mapped_column(String)
    presenting: Mapped[str] = mapped_column(String)
    hr: Mapped[int] = mapped_column(Integer)
    rr: Mapped[int] = mapped_column(Integer)
    sbp: Mapped[int] = mapped_column(Integer)
    temp: Mapped[float] = mapped_column(Float)
    spo2: Mapped[int] = mapped_column(Integer)
    ecg_flag: Mapped[int] = mapped_column(Integer)
    lab_abn: Mapped[int] = mapped_column(Integer)
    prev_ed_30d: Mapped[int] = mapped_column(Integer)
    outcome: Mapped[str] = mapped_column(String)
