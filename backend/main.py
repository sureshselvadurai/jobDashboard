from datetime import datetime, timedelta, date
from typing import List

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from jobspy import scrape_jobs
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from database import JobListing, get_db
from models import JobListingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from sqlalchemy import or_

@app.get("/jobs/", response_model=List[JobListingResponse])
def get_jobs(
    applied: bool = None,
    favourite: bool = None,
    search: str = None,  # New search filter
    db: Session = Depends(get_db),
):
    query = db.query(JobListing)

    if applied is not None:
        query = query.filter(JobListing.applied == applied)
    if favourite is not None:
        query = query.filter(JobListing.favourite == favourite)
    if search:
        query = query.filter(
            or_(
                JobListing.title.ilike(f"%{search}%")
            )
        )

    return query.order_by(JobListing.date_posted.desc()).limit(100).all()


@app.post("/jobs/")
def add_job(job: JobListingResponse, db: Session = Depends(get_db)):
    existing_job = db.query(JobListing).filter(JobListing.job_url == job.job_url).first()
    if existing_job:
        raise HTTPException(status_code=400, detail="Job already exists")

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@app.put("/jobs/{job_id}/apply")
def mark_job_applied(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.applied = True
    db.commit()
    return {"message": "Job marked as applied"}


@app.put("/jobs/{job_id}/favourite")
def mark_job_favourite(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.favourite = not job.favourite
    db.commit()
    return {"message": "Job favourite status updated"}

@app.get("/")
def mark_job_favourite():
    return {"message": "API Application is live"}


@app.get("/jobs/refresh/")
def refresh_jobs(db: Session = Depends(get_db)):
    last_24_hours = datetime.utcnow() - timedelta(hours=24)
    recent_jobs = db.query(JobListing).filter(JobListing.created_at >= last_24_hours).count()

    if recent_jobs == 0:
        new_jobs = scrape_jobs(site_name=["indeed", "linkedin", "google"],
                               search_term="software engineer",
                               google_search_term="software engineer jobs near San Francisco, CA since yesterday",
                               location="San Francisco, CA",
                               results_wanted=20,
                               hours_old=72,
                               country_indeed='USA')

        for job_data in new_jobs.to_dict(orient="records"):
            date_posted = job_data["date_posted"]

            # Ensure `date_posted` is a valid datetime
            if isinstance(date_posted, date):
                parsed_date = datetime.combine(date_posted, datetime.min.time())
            elif isinstance(date_posted, str):
                try:
                    parsed_date = datetime.strptime(date_posted, "%Y-%m-%d")
                except ValueError:
                    try:
                        parsed_date = datetime.strptime(date_posted, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        parsed_date = datetime(2000, 1, 1)
            else:
                parsed_date = datetime(2000, 1, 1)

            # ✅ Check for NaN values and replace them with "Unknown"
            job = JobListing(
                site=job_data["site"] if pd.notna(job_data["site"]) else "Unknown",
                job_url=job_data["job_url"] if pd.notna(job_data["job_url"]) else "Unknown",
                title=job_data["title"] if pd.notna(job_data["title"]) else "Unknown",
                company=job_data["company"] if pd.notna(job_data["company"]) else "Unknown",
                location=job_data["location"] if pd.notna(job_data["location"]) else "Unknown",
                date_posted=parsed_date,
                applied=False,
                favourite=False,
                description=str(job_data.get("description"))[:150] if job_data["description"] else "No description",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(job)

        db.commit()
        return {"message": "New jobs fetched and stored"}

    return {"message": "Recent jobs already exist"}