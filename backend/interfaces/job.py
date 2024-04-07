from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class JobSummary(BaseModel):
    company: str
    job_title: str
    job_nature: str
    posting_date: datetime
    deadline: datetime


class JobDetails(BaseModel):
    website: str
    company_description: str
    job_description: str
    other_requirements: Optional[str] = None
    salary: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class JobOpening(BaseModel):
    summary: JobSummary
    details: Optional[JobDetails] = None
