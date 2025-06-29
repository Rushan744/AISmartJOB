from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from .ai_recommender import get_ai_recommendations

# Database setup
Base = declarative_base()

class JobDB(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(String)

class CandidateDB(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    nom = Column(String)
    email = Column(String)
    compétences = Column(String)
    expérience = Column(Integer)
    localisation = Column(String)
    secteur = Column(String)

class MatchDB(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    score = Column(Integer)

class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str

class Candidate(BaseModel):
    id: int
    nom: str
    email: str
    compétences: str
    expérience: int
    localisation: str
    secteur: str

class Match(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    score: float

engine = create_engine('sqlite:///emploi.db')
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Security
security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == "admin" and credentials.password == "admin":
        return credentials.username
    elif credentials.username == "user" and credentials.password == "user":
        return credentials.username
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Main Endpoints
@app.get("/jobs/", response_model=List[Job])
def read_jobs(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    jobs = db.query(JobDB).all()
    return [Job(id=job.id, title=job.title, company=job.company, location=job.location, description=job.description) for job in jobs]

@app.get("/candidates/", response_model=List[Candidate])
def read_candidates(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    candidates = db.query(CandidateDB).all()
    return [Candidate(id=candidate.id, nom=candidate.nom, email=candidate.email, compétences=candidate.compétences, expérience=candidate.expérience, localisation=candidate.localisation, secteur=candidate.secteur) for candidate in candidates]

@app.get("/matches/", response_model=List[Match])
def read_matches(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    matches = db.query(MatchDB).all()
    return [Match(id=match.id, job_id=match.job_id, candidate_id=match.candidate_id, score=match.score) for match in matches]

# AI SmartJob Endpoints
ai_router = APIRouter(prefix="/ai_smartjob", tags=["AI SmartJob"])

@ai_router.get("/recommendations/{candidate_name}", response_model=List[Job])
def get_recommendations_for_candidate(
    candidate_name: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Retrieve candidate information
    print(f"Attempting to find candidate: {candidate_name}")
    candidate_db = db.query(CandidateDB).filter(CandidateDB.nom == candidate_name).first()
    if not candidate_db:
        print(f"Candidate '{candidate_name}' not found in DB.")
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_name}' not found")
    print(f"Candidate found: {candidate_db.nom}")

    candidate_info = {
        "nom": candidate_db.nom,
        "compétences": candidate_db.compétences,
        "expérience": candidate_db.expérience,
        "localisation": candidate_db.localisation,
        "secteur": candidate_db.secteur
    }
    print(f"Candidate info: {candidate_info}")

    # Retrieve all jobs
    print("Attempting to retrieve all jobs.")
    all_jobs_db = db.query(JobDB).all()
    all_jobs_list = [
        {"id": job.id, "title": job.title, "company": job.company, "location": job.location, "description": job.description}
        for job in all_jobs_db
    ]
    print(f"Retrieved {len(all_jobs_list)} jobs.")
    if not all_jobs_list:
        print("No jobs found in DB.")
        raise HTTPException(status_code=404, detail="No jobs found in database to recommend from.")

    # Get recommendations from AI model
    print("Calling AI recommender...")
    recommended_jobs_data = get_ai_recommendations(candidate_info, all_jobs_list)
    print(f"Received {len(recommended_jobs_data)} recommendations from AI model.")

    # Convert recommended job data to Pydantic Job models for response
    response_jobs = []
    for job_data in recommended_jobs_data:
        response_jobs.append(Job(**job_data))
    
    print(f"Returning {len(response_jobs)} jobs in API response.")
    return response_jobs

app.include_router(ai_router)
