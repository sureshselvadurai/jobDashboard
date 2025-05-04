import time
from sqlalchemy.exc import OperationalError

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from conf import Config
import os

Base = declarative_base()

class JobListing(Base):
    __tablename__ = "job_listings"
    __table_args__ = {"schema": "jobs"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    site = Column(String(255), nullable=True)
    job_url = Column(String(512), unique=True, nullable=True)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    date_posted = Column(DateTime, nullable=True)
    description = Column(String(5000),nullable=True)
    applied = Column(Boolean, default=True)
    favourite = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


db_url = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def wait_for_db(engine, retries=10, delay=3):
    for attempt in range(retries):
        try:
            with engine.connect():
                print("✅ Database is ready.")
                return
        except OperationalError as e:
            print(f"⏳ Waiting for DB... attempt {attempt+1}/{retries}")
            time.sleep(delay)
    raise RuntimeError("❌ Database not ready after retries.")


def init_db():
    print("Database User:", Config.DB_USER)
    wait_for_db(engine)
    Base.metadata.create_all(bind=engine)

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
