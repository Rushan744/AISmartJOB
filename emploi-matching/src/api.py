from fastapi import FastAPI, Depends, HTTPException, APIRouter, UploadFile, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import List
from pydantic import BaseModel
from .ai_recommender import get_ai_recommendations, get_ai_recommendations_from_cv
from .pdf_extractor import extract_text_from_pdf

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

class CVRecommendationResponse(BaseModel):
    recommended_jobs: List[Job]
    career_recommendation_text: str

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
@app.get(
    "/jobs/",
    response_model=List[Job],
    summary="Récupérer toutes les offres d'emploi",
    description="Récupère la liste de toutes les offres d'emploi enregistrées dans la base de données. Requiert une authentification (utilisateur ou administrateur).",
    tags=["ETL"]
)
def read_jobs(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    jobs = db.query(JobDB).all()
    return [Job(id=job.id, title=job.title, company=job.company, location=job.location, description=job.description) for job in jobs]

@app.get(
    "/candidates/",
    response_model=List[Candidate],
    summary="Récupérer tous les candidats",
    description="Récupère la liste de tous les candidats enregistrés dans la base de données. Requiert une authentification (utilisateur ou administrateur).",
    tags=["ETL"]
)
def read_candidates(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    candidates = db.query(CandidateDB).all()
    return [Candidate(id=candidate.id, nom=candidate.nom, email=candidate.email, compétences=candidate.compétences, expérience=candidate.expérience, localisation=candidate.localisation, secteur=candidate.secteur) for candidate in candidates]

@app.get(
    "/matches/",
    response_model=List[Match],
    summary="Récupérer toutes les correspondances (matches)",
    description="Récupère la liste de toutes les correspondances entre les offres d'emploi et les candidats. Requiert une authentification (utilisateur ou administrateur).",
    tags=["ETL"]
)
def read_matches(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    matches = db.query(MatchDB).all()
    return [Match(id=match.id, job_id=match.job_id, candidate_id=match.candidate_id, score=match.score) for match in matches]

# AI SmartJob Endpoints
ai_router = APIRouter(prefix="/ai_smartjob", tags=["AI SmartJob"])

@ai_router.get(
    "/recommendations/{nom_candidat}",
    response_model=List[Job],
    summary="Obtenir des recommandations d'emploi pour un candidat",
    description="Récupère une liste d'offres d'emploi recommandées pour un candidat spécifique, basée sur ses informations enregistrées. Requiert une authentification (utilisateur ou administrateur).",
    tags=["AI SmartJob"]
)
def get_recommendations_for_candidate(
    nom_candidat: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Récupérer les informations du candidat
    candidate_db = db.query(CandidateDB).filter(CandidateDB.nom == nom_candidat).first()
    if not candidate_db:
        raise HTTPException(status_code=404, detail=f"Candidat '{nom_candidat}' non trouvé")

    candidate_info = {
        "nom": candidate_db.nom,
        "compétences": candidate_db.compétences,
        "expérience": candidate_db.expérience,
        "localisation": candidate_db.localisation,
        "secteur": candidate_db.secteur
    }

    # Récupérer toutes les offres d'emploi
    all_jobs_db = db.query(JobDB).all()
    all_jobs_list = [
        {"id": job.id, "title": job.title, "company": job.company, "location": job.location, "description": job.description}
        for job in all_jobs_db
    ]
    if not all_jobs_list:
        raise HTTPException(status_code=404, detail="Aucune offre d'emploi trouvée dans la base de données pour la recommandation.")

    # Obtenir les recommandations du modèle AI
    recommended_jobs_data = get_ai_recommendations(candidate_info, all_jobs_list)

    # Convertir les données des offres d'emploi recommandées en modèles Pydantic Job pour la réponse
    response_jobs = []
    for job_data in recommended_jobs_data:
        response_jobs.append(Job(**job_data))
    
    return response_jobs

@ai_router.post(
    "/recommend_from_cv/",
    response_model=CVRecommendationResponse,
    summary="Recommander des emplois à partir d'un CV",
    description="Télécharge un fichier PDF de CV et génère des recommandations d'emploi ainsi qu'une analyse de carrière basée sur le contenu du CV. Requiert une authentification (utilisateur ou administrateur). Seuls les fichiers PDF sont supportés.",
    tags=["AI SmartJob"]
)
async def recommend_jobs_from_cv(
    fichier_cv: UploadFile = File(..., description="Le fichier PDF du CV à télécharger."),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if not fichier_cv.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont supportés.")

    try:
        cv_content = await fichier_cv.read()
        cv_text = extract_text_from_pdf(cv_content)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Impossible d'extraire le texte du PDF. Le PDF pourrait être vide ou basé sur des images.")

        # Retrieve all jobs
        all_jobs_db = db.query(JobDB).all()
        all_jobs_list = [
            {"id": job.id, "title": job.title, "company": job.company, "location": job.location, "description": job.description}
            for job in all_jobs_db
        ]
        if not all_jobs_list:
            raise HTTPException(status_code=404, detail="No jobs found in database to recommend from.")

        recommended_jobs_data, career_recommendation_text = get_ai_recommendations_from_cv(cv_text, all_jobs_list)

        response_jobs = []
        for job_data in recommended_jobs_data:
            response_jobs.append(Job(**job_data))
        
        return CVRecommendationResponse(
            recommended_jobs=response_jobs,
            career_recommendation_text=career_recommendation_text
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Une erreur interne du serveur s'est produite : {e}")

app.include_router(ai_router)
