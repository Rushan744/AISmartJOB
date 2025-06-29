# Mise en situation 1 (E1)

## Collecte, stockage et mise à disposition des données d’un projet

**Projet:** Job Matching Application - A system to match job seekers with suitable job openings.

## Formation Développeur
RNCP 37827
Promotion 2023-2024

## SOMMAIRE

1.  Introduction
2.  Présentation du projet
3.  Contexte du projet
4.  Spécifications techniques
5.  Extraction des données
    *   Données issues d’un service web (API)
    *   Données issues d’une page web
    *   Données issues d’un fichier
6.  Requêtage des données
    *   Requêtes de type SQL
7.  Agrégation des données
8.  Préparation des données
9.  Création de la base de données
    *   Modélisation des données (MCD)
    *   Modèle physique des données (MPD)
    *   Choix du système de gestion de la base données (SGBD)
    *   Création de la base de données
    *   Import des données
10. Conformité RGPD
11. Développement de l’API
    *   Spécifications fonctionnelles et techniques
    *   Conception de l’architecture de l’API
    *   Documentation
12. Perspectives et améliorations
13. Conclusions
14. Annexes

## 1. Introduction

### Présentation du projet

The Job Matching Application aims to connect job seekers with relevant job opportunities. It aggregates job postings from various sources, including a public API and web scraping, and matches them with candidate profiles based on skills, experience, and location. The application provides a way to efficiently match candidates to jobs based on a scoring system.

### Contexte du projet

This project is developed as part of a training program for developers. The goal is to demonstrate the ability to collect, store, and process data for a data-driven application. The project simulates a real-world scenario where job seekers and employers can meet each other through an automated matching process.

### Spécifications techniques

The project utilizes Python for data extraction, processing, and API development. It leverages libraries such as `requests` for API calls and web scraping, `BeautifulSoup4` for parsing HTML, `pandas` for data manipulation, `SQLAlchemy` (used as an ORM) for database interaction, and `FastAPI` for creating the API. The application uses SQLite for local data storage and MongoDB for storing job data. The project also uses GitHub for version control and collaboration.

The data flow involves extracting job data from the Adzuna API and a web scraping source, unifying this data through aggregation, and storing it in a database. Candidate data is read from a CSV file. The application then matches jobs to candidates based on predefined criteria and stores the results. The application uses HTTP Basic Authentication to secure the API endpoints.

## 2. Extraction des données

The project extracts data from the following sources:

### Données issues d’un service web (API)

Job postings are retrieved from the Adzuna API. The application sends requests to the API with specific search parameters (e.g., keywords, location) and parses the JSON response to extract relevant job details such as title, company, and location. The API key is stored in an environment variable for security.

### Données issues d’une page web

Job postings are scraped from a predefined URL using the `requests` and `BeautifulSoup4` libraries. The application extracts job title, company, and location information from the HTML content of the page.

### Données issues d’un fichier

Candidate data is read from a CSV file (`candidats.csv`). The file contains information about candidates, including their skills, experience, and location.

## 3. Requêtage des données

### Requêtes de type SQL

SQL queries are used to interact with the SQLite database. The application uses SQLAlchemy (an ORM) to define the database schema and perform CRUD operations. Queries are used to retrieve, insert, update, and delete job, candidate, and match data.

## 4. Agrégation des données

Data from the Adzuna API and the web scraping source are aggregated into a single dataset. This involves unifying the data structures and handling any inconsistencies in the data to create a coherent dataset. The aggregation process involves:

*   Fetching job data from the Adzuna API.
*   Scraping job data from the web.
*   Unifying the data from the two sources into a single list.
*   Transforming the data into Job objects.
*   Persisting the Job objects to the SQLite database.

The process of extracting data from different sources and transforming it into a consistent format can also be seen as a form of aggregation, as it involves unifying data from multiple sources into a unified dataset.

## 5. Préparation des données

Data preparation involves cleaning and transforming the extracted data to ensure consistency and accuracy. This includes:

*   Handling missing values: The application handles missing values by providing default values or skipping entries with missing data.
*   Standardizing data formats: The application standardizes data formats by converting all text to lowercase and removing whitespace.
*   Removing duplicate entries: The application removes duplicate entries by using sets to store unique values.

## 6. Création de la base de données

The application uses two databases: SQLite and MongoDB.

### SQLite Database

The SQLite database stores information about candidates, jobs, and matches. It consists of three tables:

*   **candidates:** Stores information about job seekers.
    *   `id` (INTEGER PRIMARY KEY): Candidate ID - A unique integer identifying each candidate.
    *   `nom` (TEXT): Candidate name - The full name of the candidate.
    *   `email` (TEXT): Candidate email - The email address of the candidate.
    *   `compétences` (TEXT): Candidate skills - A comma-separated list of the candidate's skills.
    *   `expérience` (INTEGER): Candidate experience - The candidate's years of experience.
    *   `localisation` (TEXT): Candidate location - The city where the candidate is located.
    *   `secteur` (TEXT): Candidate sector - The industry sector in which the candidate is seeking employment.
*   **jobs:** Stores information about job openings.
    *   `id` (INTEGER PRIMARY KEY): Job ID - A unique integer identifying each job posting.
    *   `title` (TEXT): Job title - The title of the job posting.
    *   `company` (TEXT): Job company - The name of the company offering the job.
    *   `location` (TEXT): Job location - The location of the job.
*   **matches:** Stores information about which candidates match which jobs.
    *   `id` (INTEGER PRIMARY KEY): Match ID - A unique integer identifying each match.
    *   `job_id` (INTEGER FOREIGN KEY): Job ID - A foreign key referencing the `jobs` table, indicating the job posting that is part of the match.
    *   `candidate_id` (INTEGER FOREIGN KEY): Candidate ID - A foreign key referencing the `candidates` table, indicating the candidate that is part of the match.
    *   `score` (INTEGER): Match score - A numerical score representing the quality of the match between the candidate and the job.

### MongoDB Database

The MongoDB database stores job data retrieved from the Adzuna API. The `adzuna_jobs` collection contains job postings with information such as the job's location (latitude and longitude), creation date, Adzuna Job ID, company category, location area, a URL to redirect to the job posting, the job title, and a boolean indicating if the salary is predicted.

### Modélisation des données

The database schema includes tables for jobs, candidates, and matches. Each table contains relevant fields such as job title, company, location, candidate skills, experience, and match score.

The conceptual data model (MCD) consists of three main entities: Candidate, Job, and Match. Candidates have attributes such as name, email, skills, experience, and location. Jobs have attributes such as title, company, and location. Matches represent the relationship between candidates and jobs and have a score indicating the quality of the match.

### Modèle physique des données (MPD)

Le modèle physique des données est implémenté à l'aide de SQLite. Le fichier de base de données est créé à l'aide de SQLAlchemy, un ORM. Les tables sont définies comme suit :

*   **candidates :** Stocke les informations sur les demandeurs d'emploi.
    *   `id` (INTEGER PRIMARY KEY) : ID du candidat - Un entier unique identifiant chaque candidat.
    *   `nom` (TEXT) : Nom du candidat - Le nom complet du candidat.
    *   `email` (TEXT) : Email du candidat - L'adresse email du candidat.
    *   `compétences` (TEXT) : Compétences du candidat - Une liste de compétences du candidat séparées par des virgules.
    *   `expérience` (INTEGER) : Expérience du candidat - Les années d'expérience du candidat.
    *   `localisation` (TEXT) : Localisation du candidat - La ville où se trouve le candidat.
    *   `secteur` (TEXT) : Secteur du candidat - Le secteur d'activité dans lequel le candidat recherche un emploi.
*   **jobs :** Stocke les informations sur les offres d'emploi.
    *   `id` (INTEGER PRIMARY KEY) : ID de l'emploi - Un entier unique identifiant chaque offre d'emploi.
    *   `title` (TEXT) : Titre de l'emploi - Le titre de l'offre d'emploi.
    *   `company` (TEXT) : Entreprise de l'emploi - Le nom de l'entreprise proposant l'emploi.
    *   `location` (TEXT) : Lieu de l'emploi - Le lieu de l'emploi.
*   **matches :** Stocke les informations sur les candidats qui correspondent aux emplois.
    *   `id` (INTEGER PRIMARY KEY) : ID de la correspondance - Un entier unique identifiant chaque correspondance.
    *   `job_id` (INTEGER FOREIGN KEY) : ID de l'emploi - Une clé étrangère faisant référence à la table `jobs`, indiquant l'offre d'emploi qui fait partie de la correspondance.
    *   `candidate_id` (INTEGER FOREIGN KEY) : ID du candidat - Une clé étrangère faisant référence à la table `candidates`, indiquant le candidat qui fait partie de la correspondance.
    *   `score` (INTEGER) : Score de correspondance - Un score numérique représentant la qualité de la correspondance entre le candidat et l'emploi.

### Choix du système de gestion de la base données (SGBD)

SQLite a été choisi pour sa simplicité et sa facilité d'utilisation. Il est adapté au stockage local des données et ne nécessite pas de serveur de base de données distinct. MongoDB a été choisi pour stocker les données de travail récupérées depuis l'API Adzuna, car il s'agit d'une base de données NoSQL capable de gérer de grandes quantités de données non structurées.

### Création de la base de données

The database is created using SQLAlchemy, an ORM. The application defines the table schemas and creates the tables in the SQLite database.

### Import des données

Data is imported into the database using SQLAlchemy. The application reads data from the CSV file and the combined job dataset and inserts it into the respective tables.

## 7. Conformité RGPD

From a data privacy perspective, securing the API endpoints with authentication offers several key advantages:

*   **Confidentiality:** Authentication ensures that only authorized individuals can access sensitive candidate and job data, preventing unauthorized disclosure.
*   **Integrity:** By controlling access, we minimize the risk of unauthorized modifications or deletions, helping to maintain the accuracy and reliability of the data.
*   **Controlled Access:** By implementing authentication, we ensure that only authorized personnel can interact with the API and the data it provides, limiting the potential for misuse or accidental data breaches.

## 8. Développement de l’API

The API is built using FastAPI.

### Spécifications fonctionnelles et techniques

The API provides endpoints for accessing job, candidate, and match data. It uses the REST architecture and supports JSON data format. The API endpoints are:

*   `/jobs/`: Returns a list of jobs.
*   `/candidates/`: Returns a list of candidates.
*   `/matches/`: Returns a list of matches.

The API uses HTTP Basic Authentication for security.

### Conception de l’architecture de l’API

The API is designed to be stateless and scalable. It uses authentication to protect the endpoints and ensure that only authorized users can access the data. The API follows the REST principles and uses JSON for data exchange.

### Documentation

The API is documented using OpenAPI (Swagger). The documentation includes information about the endpoints, request parameters, and response formats. The OpenAPI documentation can be accessed by navigating to `/docs` in a web browser.

## 9. Matching Logic

The matching logic is implemented by comparing the skills, location, and experience of a job and a candidate. The more skills they have in common, the closer the location, and the more the candidate's experience matches the job's requirements, the higher the match score.

The matching logic calculates a score based on common skills, location, and experience. This is a rule-based matching system.

## 10. Perspectives et améliorations

Future improvements include:

*   Implementing a more sophisticated matching algorithm: The current matching algorithm is based on a simple scoring system. A more sophisticated algorithm could take into account more factors, such as the candidate's skills, experience, and location.
*   Adding support for more data sources: The application currently extracts data from the Adzuna API and a web scraping source. Adding support for more data sources would increase the number of job postings available.
*   Improving the API documentation: The API documentation could be improved by adding more examples and explanations.
*   Implementing a user interface for managing jobs and candidates: The application currently does not have a user interface. Implementing a user interface would make it easier for users to manage jobs and candidates.
*   Implementing consent and data access/modification/deletion features to enhance data privacy.

## 11. Conclusions

The Job Matching Application demonstrates the ability to collect, store, and process data for a data-driven application. It showcases the use of various technologies and techniques for data extraction, preparation, and storage. The application provides a foundation for building a more sophisticated job matching system.

## 14. Annexes

The annexes could include more detailed information on the data sources, SQL queries, RGPD compliance information, API documentation, and coding style conventions used in the project.

### Annexe 1: Code pour la connexion à la base de données SQLite à l'aide de SQLAlchemy
```python
    engine = create_engine('sqlite:///emploi.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    ```
### Annexe 2: Code pour la définition des modèles Job, Candidate et Match à l'aide de SQLAlchemy
```python
    class Job(Base):
        __tablename__ = 'jobs'
        id = Column(Integer, primary_key=True)
        title = Column(String)
        company = Column(String)
        location = Column(String)

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
    ```
### Annexe 3: Code pour l'extraction des données de l'API Adzuna
```python
    def get_adzuna_jobs(what, where, results_per_page=10):
        params = {
            'app_id': '0dce7689',
            'app_key': ADZUNA_API_KEY,
            'what': what,
            'where': where,
            'results_per_page': results_per_page,
            'content-type': 'application/json'
        }
        response = requests.get(ADZUNA_API_URL, params=params)
        response.raise_for_status()
        return response.json()['results']
    ```
### Annexe 4: Code pour l'extraction des données du web
```python
    def extract_from_web():
        url = "https://realpython.github.io/fake-jobs/"
        scraped_data = []
        try:
            response = requests.get(url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.content, "html.parser")
            job_listings = soup.find_all("div", class_="card-content")

            for job in job_listings:
                title = job.find("h2", class_="title is-5").text.strip() if job.find("h2", class_="title is-5") else ""
                company = job.find("h3", class_="subtitle is-6 company").text.strip() if job.find("h3", class_="subtitle is-6 company") else ""
                location = job.find("p", class_="location").text.strip() if job.find("p", class_="location") else ""

                # Combine company and location for the description
                description = f"{company} - {location}" if company and location else company or location or "N/A"
            
                # Assign category using the refactored function
                category = assign_category_from_text(title, description)

                scraped_data.append({
                    "title": title,
                    "description": description,
                    "category": category
                })

            # Example print to verify
            print("✅ Example scraped job:", scraped_data[0] if scraped_data else "No jobs scraped")
            return scraped_data

        except requests.exceptions.RequestException as e:
            print(f"❌ Error scraping web data: {e}")
            return []
    ```
### Annexe 5: Code pour la logique de correspondance
```python
    def match_job_to_candidate(job, candidate):
        job_skills = [s.strip() for s in re.split(r',\s*', job.get('skills', '').lower())]
        candidate_skills = [s.strip() for s in re.split(r',\s*', candidate.get('compétences', '').lower())]
        common_skills = set(job_skills) & set(candidate_skills)
        skill_score = len(common_skills)

        job_location = job.get('location', {}).get('display_name', '').lower()
        candidate_location = candidate.get('localisation', '').lower()
        if job_location in candidate_location:
            location_score = 0.5  # Partial score for containing location
        elif candidate_location in job_location:
            location_score = 0.5
        else:
            location_score = 0

        # Experience score
        job_experience = job.get('experience_min', 0)
        candidate_experience = candidate.get('expérience', 0)
        experience_score = 0
        if candidate_experience >= job_experience:
            experience_score = 1
            if candidate_experience - job_experience > 5:
                experience_score += 0.5  # Bonus for significantly more experience

        total_score = skill_score + location_score + experience_score
        return total_score
    ```
### Annexe 6: Code pour la connexion à MongoDB
```python
    MONGO_URI = "mongodb://localhost:27017/"  # Replace with your MongoDB URI
    client = pymongo.MongoClient(MONGO_URI)
    db = client["emploi_matching"]  # Replace with your database name
    jobs_collection = db["adzuna_jobs"]
    ```
### Annexe 7: Code pour la configuration de FastAPI
```python
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

    # Endpoints
    @app.get("/jobs/", response_model=List[Job])
    def read_jobs(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
        jobs = db.query(JobDB).all()
        return [Job(id=job.id, title=job.title, company=job.company, location=job.location) for job in jobs]

    @app.get("/candidates/", response_model=List[Candidate])
    def read_candidates(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
        candidates = db.query(CandidateDB).all()
        return [Candidate(id=candidate.id, nom=candidate.nom, email=candidate.email, compétences=candidate.compétences, expérience=candidate.expérience, localisation=candidate.localisation, secteur=candidate.secteur) for candidate in candidates]

    @app.get("/matches/", response_model=List[Match])
    def read_matches(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
        matches = db.query(MatchDB).all()
        return [Match(id=match.id, job_id=match.job_id, candidate_id=match.candidate_id, score=match.score) for match in matches]
