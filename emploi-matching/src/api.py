from fastapi import FastAPI, Depends, HTTPException, APIRouter, UploadFile, File, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import List
from pydantic import BaseModel
from .ai_recommender import get_ai_recommendations, get_ai_recommendations_from_cv, extract_skills_with_scores_from_cv
from .pdf_extractor import extract_text_from_pdf
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from passlib.context import CryptContext

# Database setup
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

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

class SkillScore(BaseModel):
    skill: str
    score: int

class SkillsExtractionResponse(BaseModel):
    extracted_skills: List[SkillScore]

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

class CVRecommendationResponse(BaseModel):
    recommended_jobs: List[Job]
    career_recommendation_text: str

engine = create_engine('sqlite:///emploi.db')
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()



# Security
security = HTTPBasic()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = get_user(db, credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

# Main Endpoints
@app.get(
    "/jobs/",
    response_model=List[Job],
    summary="Récupérer toutes les offres d'emploi",
    description="Récupère la liste de toutes les offres d'emploi enregistrées dans la base de données. Requiert une authentification (utilisateur ou administrateur).",
    tags=["ETL"]
)
def read_jobs(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    jobs = db.query(JobDB).all()
    return [Job(id=job.id, title=job.title, company=job.company, location=job.location, description=job.description) for job in jobs]

@app.get(
    "/candidates/",
    response_model=List[Candidate],
    summary="Récupérer tous les candidats",
    description="Récupère la liste de tous les candidats enregistrés dans la base de données. Requiert une authentification (utilisateur ou administrateur).",
    tags=["ETL"]
)
def read_candidates(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    candidates = db.query(CandidateDB).all()
    return [Candidate(id=candidate.id, nom=candidate.nom, email=candidate.email, compétences=candidate.compétences, expérience=candidate.expérience, localisation=candidate.localisation, secteur=candidate.secteur) for candidate in candidates]

@app.get(
    "/matches/",
    response_model=List[Match],
    summary="Récupérer toutes les correspondances (matches)",
    description="Récupère la liste de toutes les correspondances entre les offres d'emploi et les candidats. Requiert une authentification (utilisateur ou administrateur).",
    tags=["ETL"]
)
def read_matches(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    matches = db.query(MatchDB).all()
    return [Match(id=match.id, job_id=match.job_id, candidate_id=match.candidate_id, score=match.score) for match in matches]

# User Management Endpoints
user_router = APIRouter(prefix="/users", tags=["User Management"])

@user_router.post(
    "/",
    response_model=User,
    summary="Créer un nouvel utilisateur",
    description="Enregistre un nouvel utilisateur avec un nom d'utilisateur et un mot de passe haché. Accessible à tous.",
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return User(id=db_user.id, username=db_user.username)

@user_router.get(
    "/",
    response_model=List[User],
    summary="Récupérer tous les utilisateurs",
    description="Récupère la liste de tous les utilisateurs enregistrés. Requiert une authentification (administrateur uniquement).",
)
def read_users(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    if current_user.username != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can view all users")
    users = db.query(UserDB).all()
    return [User(id=user.id, username=user.username) for user in users]

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
    current_user: UserDB = Depends(get_current_user)
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
    current_user: UserDB = Depends(get_current_user)
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

@ai_router.post(
    "/extract_skills_from_cv/",
    response_model=SkillsExtractionResponse,
    summary="Extraire les compétences d'un CV avec des scores",
    description="Télécharge un fichier PDF de CV et extrait 10 compétences clés avec un score de pertinence (0-100) pour chacune. Requiert une authentification (utilisateur ou administrateur). Seuls les fichiers PDF sont supportés.",
    tags=["AI SmartJob"]
)
async def extract_skills_from_cv_endpoint(
    fichier_cv: UploadFile = File(..., description="Le fichier PDF du CV à télécharger."),
    current_user: UserDB = Depends(get_current_user)
):
    if not fichier_cv.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont supportés.")

    try:
        cv_content = await fichier_cv.read()
        cv_text = extract_text_from_pdf(cv_content)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Impossible d'extraire le texte du PDF. Le PDF pourrait être vide ou basé sur des images.")

        extracted_skills = extract_skills_with_scores_from_cv(cv_text)
        
        return SkillsExtractionResponse(extracted_skills=extracted_skills)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Une erreur interne du serveur s'est produite : {e}")

app.include_router(user_router)
app.include_router(ai_router)

# Serve static files (your frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse, summary="Servir la page d'accueil du frontend", description="Accède à la page HTML principale de l'application frontend.")
async def read_root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")
