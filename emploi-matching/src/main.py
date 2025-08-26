import os
import pandas as pd
from dotenv import load_dotenv
from scraping import extract_from_web
from matching import match_job_to_candidate
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base
import pymongo
from generate_candidates import generate_candidates_csv

load_dotenv()

MONGO_URI = "mongodb://localhost:27017/" 
client = pymongo.MongoClient(MONGO_URI)
db = client["emploi_matching"]  
jobs_collection = db["adzuna_jobs"]

# Database setup
Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(String)

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    nom = Column(String)
    email = Column(String)
    compétences = Column(String)
    expérience = Column(Integer)
    localisation = Column(String)
    secteur = Column(String)

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    score = Column(Integer)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///emploi.db")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def get_adzuna_jobs_data():
    from api_jobs import get_adzuna_jobs
    adzuna_jobs = get_adzuna_jobs(what='developer', where='Paris')
    return adzuna_jobs

def main():
    import os
    print(os.getcwd())

    # Generate new candidate data
    generate_candidates_csv()

    # Clear and insert data into MongoDB
    jobs_collection.delete_many({})
    adzuna_jobs = get_adzuna_jobs_data()
    jobs_collection.insert_many(adzuna_jobs)

    # Scrape job data from web
    scraped_data = extract_from_web()
    print(f"Scraped data: {scraped_data}")

    # Load candidate data from CSV
    csv_path = 'D:\AISmartJOB\emploi-matching\data\candidats.csv'
    print(f"Attempting to read candidates from CSV: {csv_path}")
    candidates_df = pd.read_csv(csv_path)
    candidates = candidates_df.to_dict('records')
    print(f"Successfully read {len(candidates)} candidates from CSV.")

    # Clear and insert data into SQLite jobs table
    # Combine data from web scraping and adzuna api
    combined_jobs = scraped_data + adzuna_jobs

    Job.__table__.drop(engine)
    Base.metadata.create_all(engine)

    # Create Job objects and add to session
    # Normalize job data before inserting into SQLite and matching
    normalized_jobs = []
    for job_data in combined_jobs:
        location = ''
        company = ''
        if 'location' in job_data:
            if isinstance(job_data['location'], dict) and 'display_name' in job_data['location']:
                location = job_data['location']['display_name']
            elif isinstance(job_data['location'], str):
                location = job_data['location']
        
        if 'company' in job_data:
            if isinstance(job_data['company'], dict) and 'display_name' in job_data['company']:
                company = job_data['company']['display_name']
            elif isinstance(job_data['company'], str):
                company = job_data['company']
        
        description = job_data.get('description', '')
        
        normalized_job = {
            "title": job_data.get('title', ''),
            "company": company,
            "location": location,
            "description": description,
            "category": job_data.get('category', '') # Keep category for matching if needed
        }
        normalized_jobs.append(normalized_job)

    # Clear and insert data into SQLite jobs table
    Job.__table__.drop(engine)
    Base.metadata.create_all(engine)

    # Create Job objects and add to session
    for job in normalized_jobs:
        new_job = Job(title=job['title'], company=job['company'], location=job['location'], description=job['description'])
        session.add(new_job)
    session.commit()

    # Clear existing matches
    session.query(Match).delete()
    session.commit()

    # Clear existing data in Candidate and Match tables
    session.query(Candidate).delete()
    session.query(Match).delete()
    session.commit()

    # New matching logic using AI model
    for candidate_data in candidates:
        # Create Candidate object and add to session
        new_candidate = Candidate(
            id=candidate_data['id'],
            nom=candidate_data['nom'],
            email=candidate_data['email'],
            compétences=candidate_data['compétences'],
            expérience=candidate_data['expérience'],
            localisation=candidate_data['localisation'],
            secteur=candidate_data['secteur']
        )
        session.add(new_candidate)
        try:
            session.commit()
            print(f"Inserted candidate: {new_candidate.nom} (ID: {new_candidate.id})")
        except Exception as e:
            session.rollback()
            print(f"Error inserting candidate {new_candidate.nom}: {e}")

        for job_data in normalized_jobs: # Use normalized_jobs here
            score = match_job_to_candidate(job_data, candidate_data)
            print(f"Matching score for {candidate_data['nom']} and {job_data['title']}: {score}")

            # Find the Job object in the database
            db_job = session.query(Job).filter_by(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location']
            ).first()
            
            if db_job:
                new_match = Match(job_id=db_job.id, candidate_id=new_candidate.id, score=score)
                session.add(new_match)
                session.commit()
            else:
                print(f"Warning: Job '{job_data['title']}' not found in DB for matching. Match not saved.")
    
    # Verify candidates in DB after insertion
    num_candidates_in_db = session.query(Candidate).count()
    print(f"Total candidates in database after insertion: {num_candidates_in_db}")

if __name__ == '__main__':
    main()
