from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class JobListing(Base):
    __tablename__ = "job_listings"

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

# DB_USER = os.getenv("DB_USER", "root")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = os.getenv("DB_PORT", "3306")
# DB_NAME = os.getenv("DB_NAME", "job_database")

DB_USER = os.getenv("DB_USER", "admin")  # Replace with your actual DB user
DB_PASSWORD = os.getenv("DB_PASSWORD", "Sureshraja5*")  # Replace with your actual DB password
DB_HOST = os.getenv("DB_HOST", "database-1.cgf47yzycfda.us-east-1.rds.amazonaws.com")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "database-1")  # Replace with your actual DB name

db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
