import time
import os
from datetime import datetime
from sqlalchemy.exc import OperationalError
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from conf import Config

import pymysql

Base = declarative_base()

class JobListing(Base):
    __tablename__ = "job_listings"
    __table_args__ = {"schema": "jobs"}  # Remove this if not using MySQL schemas

    id = Column(Integer, primary_key=True, autoincrement=True)
    site = Column(String(255), nullable=True)
    job_url = Column(String(512), unique=True, nullable=True)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    date_posted = Column(DateTime, nullable=True)
    description = Column(String(5000), nullable=True)
    applied = Column(Boolean, default=True)
    favourite = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Construct DB URL
db_url = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
masked_url = db_url.replace(Config.DB_PASSWORD, "*****")
print(f"🔗 Connecting to DB URL: {masked_url}")

# Raw pymysql connectivity check
try:
    print("🔍 Testing raw pymysql connection...")
    pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=int(Config.DB_PORT),
        connect_timeout=5
    )
    print("✅ Raw pymysql connection succeeded.")
except Exception as e:
    print(f"❌ Raw pymysql connection failed: {e}")

# SQLAlchemy setup
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def wait_for_db(engine, retries=10, delay=3):
    for attempt in range(retries):
        try:
            with engine.connect():
                print("✅ SQLAlchemy engine connected.")
                return
        except OperationalError as e:
            print(f"C {masked_url}: ⏳ Waiting for DB... attempt {attempt+1}/{retries} - error: {e}")
            time.sleep(delay)
    raise RuntimeError("❌ Database not ready after retries.")

def init_db():
    print("🛠️ Initializing DB...")
    wait_for_db(engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created (if not exist).")

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
