import os
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, date
from typing import List

import pandas as pd
import requests
from fastapi import FastAPI, Depends, HTTPException
from jobspy import scrape_jobs
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from database import JobListing, get_db
from models import JobListingResponse
from conf import Config
import os
import requests
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from sqlalchemy import or_

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/routes")
def list_routes():
    return [route.path for route in app.routes]

@app.get("/jobs/", response_model=List[JobListingResponse])
def get_jobs(
    applied: bool = None,
    favourite: bool = None,
    search: str = None,
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
    search_list = ["software engineer","machine learning"]

    for search_term in search_list:
        if recent_jobs == 0:
            new_jobs = scrape_jobs(site_name=["linkedin"],
                                   search_term=search_term,
                                   google_search_term=f"{search_term} jobs near San Francisco, CA since yesterday",
                                   location="San Francisco, CA",
                                   results_wanted=30,
                                   hours_old=24,
                                   country_indeed='USA')

            for job_data in new_jobs.to_dict(orient="records"):
                date_posted = job_data["date_posted"]
                job_url = job_data.get("job_url")

                existing_job = db.query(JobListing).filter(JobListing.job_url == job_url).first()

                if existing_job:
                    continue
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

        try:
            jobs = get_jobs(db=db)
            top_jobs = jobs[:10]
            logger.info(f"📋 Retrieved {len(top_jobs)} jobs")
        except Exception as e:
            logger.error(f"❌ Failed to fetch jobs: {e}")
            return JSONResponse(status_code=500, content={"error": "Failed to fetch jobs"})

        # 3. Format Slack message
        message = "*🆕 Top 10 Latest Jobs*\n"
        if not top_jobs:
            message += "No jobs available."
        else:
            for idx, job in enumerate(top_jobs, 1):
                message += f"\n{idx}. *{job.title}* at *{job.company}*\n<{job.job_url}|View Job>"

        # 4. Send to notifier
        try:
            logger.info(f"📨 Sending Slack message to {Config.NOTIFIER_URL}")
            res = requests.post(Config.NOTIFIER_URL, json={"text": message})
            if res.status_code != 200:
                logger.error(f"❌ Slack response: {res.status_code}, {res.text}")
                return JSONResponse(status_code=500, content={"error": "Slack webhook failed"})
        except Exception as e:
            logger.error(f"❌ Exception while sending Slack message: {e}")
            return JSONResponse(status_code=500, content={"error": str(e)})

        return {"message": "Jobs refreshed and Slack notified", "jobs_sent": len(top_jobs)}

    return {"message": "Recent jobs already exist"}


@app.get("/notify/refresh-and-notify")
def refresh_and_notify(db: Session = Depends(get_db)):
    logger.info("🔄 Called /notify/refresh-and-notify/")

    # 1. Refresh jobs
    try:
        logger.info("🔁 Refreshing jobs")
        refresh_jobs(db)
    except Exception as e:
        logger.error(f"❌ Failed to refresh jobs: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to refresh jobs"})

    # 2. Get latest 10 jobs
    try:
        jobs = get_jobs(db=db)
        top_jobs = jobs[:10]
        logger.info(f"📋 Retrieved {len(top_jobs)} jobs")
    except Exception as e:
        logger.error(f"❌ Failed to fetch jobs: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to fetch jobs"})

    # 3. Format Slack message
    message = "*🆕 Top 10 Latest Jobs*\n"
    if not top_jobs:
        message += "No jobs available."
    else:
        for idx, job in enumerate(top_jobs, 1):
            message += f"\n{idx}. *{job.title}* at *{job.company}*\n<{job.job_url}|View Job>"

    # 4. Send to notifier
    try:
        logger.info(f"📨 Sending Slack message to {Config.NOTIFIER_URL}")
        res = requests.post(Config.NOTIFIER_URL, json={"text": message})
        if res.status_code != 200:
            logger.error(f"❌ Slack response: {res.status_code}, {res.text}")
            return JSONResponse(status_code=500, content={"error": "Slack webhook failed"})
    except Exception as e:
        logger.error(f"❌ Exception while sending Slack message: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {"message": "Jobs refreshed and Slack notified", "jobs_sent": len(top_jobs)}
