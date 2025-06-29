# Mise en situation 1 (E1)

Collecte, stockage et mise à disposition des données d’un projet IA

Projet IA: SmartJob

Formation Développeur en Intelligence Artificielle

RNCP 37827
Promotion 2023-2025

RUSHAN ZAMIR Saeedullah

SOMMAIRE

1.  Introduction
    *   Présentation du projet
    *   Contexte du projet
    *   Spécifications techniques
2.  Extraction des données
    *   Données issues d’un service web (API)
    *   Données issues d’une page web
    *   Données issues d’un fichier
3.  Requêtage des données
    *   Requêtes de type SQL
4.  Agrégation des données
5.  Préparation des données
6.  Création de la base de données
    *   Modélisation des données
    *   Modèle physique des données (MPD)
    *   Choix du système de gestion de la base données (SGBD)
    *   Création de la base de données
    *   Import des données
7.  Conformité RGPD
8.  Développement de l’API
    *   Spécifications fonctionnelles et techniques
    *   Conception de l’architecture de l’API
    *   Documentation
9.  Matching Logic
10. Perspectives et améliorations
11. Conclusions
12. Annexes

## 1. Introduction

### Présentation du projet

L'application Job Matching vise à mettre en relation les demandeurs d'emploi avec des offres d'emploi pertinentes. Elle agrège les offres d'emploi provenant de diverses sources, notamment une API publique et des analyses web, et les met en relation avec les profils de candidats en fonction de leurs compétences, de leur expérience et de leur localisation. L'application permet de mettre efficacement en relation les candidats et les offres d'emploi grâce à un système de notation.

### Contexte du projet

Ce projet s'inscrit dans le cadre d'un programme de formation destiné aux développeurs en Intelligence Artificielle. Son objectif est de démontrer la capacité à collecter, stocker et traiter des données pour une application data-driven. Il simule un scénario réel où les demandeurs d'emploi et les employeurs peuvent se rencontrer grâce à un processus de mise en relation automatisé.

### Spécifications techniques

Le projet utilise Python pour l'extraction et le traitement des données, ainsi que pour le développement d'API. Il s'appuie sur des library telles que « requests » pour les appels d'API et le web scraping, « BeautifulSoup4 » pour l'analyse HTML, « pandas » pour la manipulation des données, « SQLAlchemy » pour l'interaction avec les bases de données et « FastAPI » pour la création de l'API. L'application utilise SQLite pour le stockage local des données et MongoDB pour le stockage des données de jobs. Le projet utilise également GitHub pour le contrôle des versions et la collaboration.

**GitHub Repository:** [https://github.com/Rushan744/Smartjob.git](https://github.com/Rushan744/Smartjob.git)

Le flux de données consiste à extraire les données d'emploi de l'API Adzuna et d'une source web scraping, à combiner ces données et à les stocker dans une base de données. Les données des candidats sont lues à partir d'un fichier CSV. L'application associe ensuite les offres d'emploi aux candidats selon des critères prédéfinis et stocke les résultats. L'application utilise l'authentification HTTP de base pour sécuriser les points de terminaison de l'API.

Technologies, Outils et Services Externes:

Pour le traitement de ces données et la mise en place de la pipeline, la programmation est réalisée en Python. Les outils et librairies Python utilisés incluent :

*   `requests` : pour interagir avec les API REST et récupérer les données.
*   `BeautifulSoup4` : pour l'analyse du contenu HTML extrait des pages web, permettant d'extraire les informations pertinentes.
*   `pandas` : pour la manipulation et le traitement des données, permettant une analyse et une transformation efficaces des données.
*   `SQLAlchemy` (utilisé comme ORM) : pour l'interaction avec la base de données SQLite, facilitant l'extraction et l'importation des données. Il permet de définir le schéma de la base de données et d'effectuer des opérations CRUD de manière object-relationnelle.
*   `FastAPI` : Un framework web moderne, rapide (haute performance) pour la construction d'API, offrant des fonctionnalités telles que la validation des données et la génération automatique de documentation.
*   `PyMongo` : pour se connecter à MongoDB et stocker les données des offres d'emploi.
*   `Faker` : pour générer des données factices pour les candidats, utilisées à des fins de test et de développement.

## 2. Extraction des données

Le projet extrait des données des sources suivantes :

### Données issues d’un service web (API)

Les offres d'emploi sont récupérées depuis l'API Adzuna. L'application envoie des requêtes à l'API avec des paramètres de recherche spécifiques (par exemple, mots-clés, localisation) et analyse la réponse JSON pour extraire les informations pertinentes sur le poste, telles que l'intitulé, l'entreprise et la localisation. La clé API est stockée dans une variable d'environnement pour des raisons de sécurité.

**Example:** The Adzuna API provides structured job data, including fields like `title`, `company`, `location`, `salary`, and `description`. For instance, a query for "Data Scientist" in "Paris" would return a JSON response containing multiple job postings with these fields populated.

### Données issues d’une page web

Les offres d'emploi sont extraites d'une URL prédéfinie à l'aide des bibliothèques « requests » et « BeautifulSoup4 ». L'application extrait les informations relatives au poste, à l'entreprise et à la localisation du contenu HTML de la page.

**Example:** Web scraping is used to extract job postings from the "Real Python Fake Jobs" website. The scraper targets specific HTML elements (e.g., `<h2>` for job title, `<h3>` for company) and extracts the text content. This method is useful when the data source doesn't provide a direct API.

### Données issues d’un fichier

Les données des candidats sont extraites d'un fichier CSV (« candidats.csv »). Ce fichier contient des informations sur les candidats, notamment leurs compétences, leur expérience et leur localisation.

## 3. Requêtage des données

### Requêtes de type SQL

Les requêtes SQL permettent d'interagir avec la base de données SQLite. L'application utilise SQLAlchemy(an ORM) pour définir le schéma de la base de données et effectuer des opérations CRUD. Les requêtes permettent de récupérer, d'insérer, de mettre à jour et de supprimer des données d'emploi, de candidat et de correspondance.

## 4. Agrégation des données

Les données de l'API et de la source de scraping web sont combinées en un seul ensemble de données. Cela implique la normalisation des structures de données et la gestion des éventuelles incohérences. Le processus d'agrégation comprend :

*   Récupération des données de jobs à partir de l'API Adzuna(Mongodb).
*   Extraction de données de travail à partir du Web.
*   Combiner les données des deux sources dans une seule liste.
*   Parcourir la liste combinée et créer des objets Job pour chaque offre d'emploi.
*   Ajout des objets Job à la base de données SQLite.

**Examples:**

*   The `title` field from Adzuna API might be named `title` while in the scraped data it might be `job_title`. Aggregation involves renaming or mapping these fields to a common name.
*   The `location` field might be a nested dictionary in the API response but a simple string in the scraped data. Aggregation involves transforming the data into a consistent format.

Le processus d’extraction de données provenant de différentes sources et de leur transformation en un format cohérent peut également être considéré comme une forme d’agrégation, car il implique de combiner des données provenant de plusieurs sources dans un ensemble de données unifié.

## 5. Préparation des données

La préparation des données implique le nettoyage et la transformation des données extraites afin d'en garantir la cohérence et l'exactitude. Cela comprend :

*   Gestion des valeurs manquantes : l'application gère les valeurs manquantes en fournissant des valeurs par défaut ou en ignorant les entrées contenant des données manquantes.
*   Normalisation des formats de données : l'application normalise les formats de données en convertissant tout le texte en minuscules et en supprimant les espaces.

## 6. Création de la base de données

L'application utilise deux bases de données : SQLite et MongoDB.

### Base de données SQLite

La base de données SQLite stocke les informations sur les candidats, les offres d'emploi et les correspondances. Elle se compose de trois tables :

La table « matches » utilise les clés étrangères « job_id » et « candidate_id » pour référencer respectivement les tables « jobs » et « candidates ». Cela permet à l'application de récupérer efficacement toutes les correspondances pour un poste ou un candidat donné.

### Base de données MongoDB

The MongoDB database stores job data retrieved from the Adzuna API. The `adzuna_jobs` collection contains job postings with information such as the job's location (latitude and longitude), creation date, Adzuna Job ID, company category, location area, a URL to redirect to the job posting, the job title, and a boolean indicating if the salary is predicted.

**MongoDB Usage Explanation:** MongoDB is used to store the raw job data retrieved from the Adzuna API because it is a NoSQL database that can handle large amounts of unstructured data. The data is stored in MongoDB as it is received from the API. However, for the matching process and to maintain consistency with the candidate data (stored in SQLite), the relevant job data is extracted from MongoDB and transferred to the SQLite database. This approach allows us to leverage the flexibility of MongoDB for data ingestion and the relational structure of SQLite for data analysis and matching.

### Modélisation conceptuelle des données (MCP)

The database schema includes tables for jobs, candidates, and matches. Each table contains relevant fields such as the job title, company, location, candidate skills, experience, and match score.

**Merise Method Explanation:**

The Merise method was used to design the database schema. This method involves three steps:

1.  **Conceptual Data Model (CDM):** This model identifies the entities (Candidate, Job, Match) and their relationships.
2.  **Logical Data Model (LDM):** This model defines the attributes of each entity and the relationships between them.
3.  **Physical Data Model (PDM):** This model defines the tables, columns, data types, primary keys, and foreign keys in the database.

The three tables (candidates, jobs, matches) were chosen to represent the core entities and relationships in the job matching application. The fields in each table were chosen to store the relevant information about each entity. The primary keys were chosen to uniquely identify each record in the table. The foreign keys were chosen to represent the relationships between the tables.

*   **candidates :** Stocke les informations sur les demandeurs d'emploi.
    *   `id` (INTEGER PRIMARY KEY) : ID du candidat - Un entier unique identifiant chaque candidat.
    *   `nom` (TEXT) : Nom du candidat - Le nom complet du candidat.
    *   Email` (TEXT) : Email du candidat - L'adresse email du candidat.
    *   `compétences` (TEXT) : Compétences du candidat - Une liste de compétences du candidat séparées par des virgules.
    *   `expérience` (INTEGER) : Expérience du candidat - Les années d'expérience du candidat.
    *   `localisation` (TEXT) : Localisation du candidat - La ville où se trouve le candidat.
    *   'Secteur` (TEXT) : Secteur du candidat - Le secteur d'activité dans lequel le candidat recherche un emploi.
*   **jobs :** Stocke les informations sur les offres d'emploi.
    *   `id` (INTEGER PRIMARY KEY) : ID de l'emploi - Un entier unique identifiant chaque offre d'emploi.
    *   `title` (TEXT) : Titre de l'emploi - Le titre de l'offre d'emploi.
    *   `company` (TEXT) : Entreprise de l'emploi - Le nom de l'entreprise proposant l'emploi.
    *   'Location` (TEXT) : Lieu de l'emploi - Le lieu de l'emploi.
*   **matches :** Stocke les informations sur les candidats qui correspondent aux emplois.
    *   `id` (INTEGER PRIMARY KEY) : ID de la correspondance - Un entier unique identifiant chaque correspondance.
    *   `job_id` (INTEGER FOREIGN KEY) : ID de l'emploi - Une clé étrangère faisant référence à la table `jobs`, indiquant l'offre d'emploi qui fait partie de la correspondance.
    *   `candidate id` (INTEGER FOREIGN KEY) : ID du candidat - Une clé étrangère faisant référence à la table `candidates`, indiquant le candidat qui fait partie de la correspondance.
    *   `Score` (INTEGER) : Score de correspondance - Un score numérique représentant la qualité de la correspondance entre le candidat et l'emploi.

### Modèle physique des données (MPD)

Le modèle physique des données est implémenté à l'aide de SQLite. Le fichier de base de données est créé à l'aide de SQLAlchemy, un ORM. Les tables sont définies comme suit :

Choix du système de gestion de la base données (SGBD)

SQLite a été choisi pour sa simplicité et sa facilité d'utilisation. Il est adapté au stockage local des données et ne nécessite pas de serveur de base de données distinct. MongoDB a été choisi pour stocker les données de travail récupérées depuis l'API Adzuna, car il s'agit d'une base de données NoSQL capable de gérer de grandes quantités de données non structurées.

Création de la base de données

La base de données est créée avec SQLAlchemy. L'application définit les schémas des tables et crée les tables dans la base de données SQLite.

Import des données

Les données sont importées dans la base de données via SQLAlchemy. L'application lit les données du fichier CSV et de l'ensemble de données de travail combiné, puis les insère dans les tables correspondantes.

## 7. Conformité RGPD

Du point de vue de la confidentialité des données, la sécurisation des points de terminaison de l'API avec authentification offre plusieurs avantages clés :

*Confidentialité:L'authentification garantit que seules les personnes autorisées peuvent accéder aux données sensibles des candidats et des emplois, empêchant ainsi toute divulgation non autorisée.
*Intégrité:En contrôlant l’accès, nous minimisons le risque de modifications ou de suppressions non autorisées, contribuant ainsi à maintenir l’exactitude et la fiabilité des données.
*Accès contrôlé :En mettant en œuvre l’authentification, nous garantissons que seul le personnel autorisé peut interagir avec l’API et les données qu’elle fournit, limitant ainsi le risque d’utilisation abusive ou de violation accidentelle des données.

**RGPD Compliance Details:**

As the application stores candidate names and email addresses, it is subject to RGPD (General Data Protection Regulation) requirements. The following measures must be taken to ensure compliance:

*   **Data Retention:** Data should be stored only for as long as necessary to fulfill the purpose for which it was collected.
*   **Purpose of Processing:** The purpose of processing personal data (name, email) must be clearly defined (e.g., matching candidates to jobs).
*   **User Consent:** Users must provide explicit consent for their data to be collected and processed.
*   **Data Security:** Implement appropriate technical and organizational measures to protect personal data against unauthorized access, loss, or destruction.
*   **Data Access and Modification:** Users must have the right to access, modify, and delete their personal data.

## 8. Développement de l’API

L'API est construite à l'aide de FastAPI.

Spécifications fonctionnelles et techniques

L'API fournit des points de terminaison pour accéder aux données d'offres d'emploi, de candidats et de correspondances. Elle utilise l'architecture REST et prend en charge le format de données JSON. Les points de terminaison de l'API sont :

*   `/jobs/` : renvoie une liste de tâches.
*   `/candidates/`: renvoie une liste de candidats.
*   `/matches/` : renvoie une liste de correspondances.

L'API utilise l'authentification HTTP de base pour la sécurité.

Conception de l’architecture de l’API

L'API est conçue pour être sans état et évolutive. Elle utilise l'authentification pour protéger les points de terminaison et garantir que seuls les utilisateurs autorisés peuvent accéder aux données. L'API suit les principes REST et utilise JSON pour l'échange de données.

Documentation

L'API est documentée via OpenAPI (Swagger). Cette documentation comprend des informations sur les points de terminaison, les paramètres de requête et les formats de réponse. Elle est accessible via le répertoire « /docs » d'un navigateur web.

9. Logique de correspondance

La logique de correspondance est mise en œuvre en comparant les compétences, le lieu et l'expérience d'un poste et d'un candidat. Plus les compétences sont communes, plus le lieu est proche et plus l'expérience du candidat correspond aux exigences du poste, plus le score de correspondance est élevé.

La logique de correspondance calcule un score basé sur des compétences, une localisation et une expérience communes. Il s'agit d'un système de correspondance basé sur des règles.

10. Perspectives et améliorations

Les améliorations futures incluent :

* Mise en œuvre d'un algorithme de sélection plus sophistiqué : l'algorithme actuel repose sur un système de notation simple. Un algorithme plus sophistiqué pourrait prendre en compte davantage de facteurs, tels que les compétences, l'expérience et la localisation du candidat.
* Amélioration de la documentation de l'API : La documentation de l'API pourrait être améliorée en ajoutant plus d'exemples et d'explications.
* Implémentation d'une interface utilisateur pour la gestion des offres d'emploi et des candidats : L'application ne dispose actuellement d'aucune interface utilisateur. L'implémentation d'une interface utilisateur faciliterait la gestion des offres d'emploi et des candidats.

11. Conclusions

L'application de recherche d'emploi démontre la capacité de collecter, stocker et traiter des données pour une application axée sur les données. Elle illustre l'utilisation de diverses technologies et techniques d'extraction, de préparation et de stockage des données. Elle constitue le fondement d'un système de recherche d'emploi plus sophistiqué.

12. Annexes

**Annexe 1: Code pour la connexion à la base de données SQLite à l'aide de SQLAlchemy**

```python
engine = create_engine('sqlite:///emploi.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
```

**Annexe 2: Code pour la définition des modèles Job, Candidate et Match à l'aide de SQLAlchemy**

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

**Annexe 3: Code pour l'extraction des données de l'API Adzuna**

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

**Annexe 4: Code pour l'extraction des données du web**

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

**Annexe 5: Code pour la logique de correspondance**

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

**Annexe 6: Code pour la connexion à MongoDB**

```python
MONGO_URI = "mongodb://localhost:27017/"  # Replace with your MongoDB URI
client = pymongo.MongoClient(MONGO_URI)
db = client["emploi_matching"]  # Replace with your database name
jobs_collection = db["adzuna_jobs"]
```

**Annexe 7: Code pour la configuration de FastAPI**

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
```

**Annexe 8: Example Job Postings**

```json
[
  {
    "title": "Software Engineer",
    "company": "Google",
    "location": "Paris",
    "skills": ["Python", "Java", "SQL"],
    "description": "We are looking for a Software Engineer to join our team in Paris."
  },
  {
    "title": "Data Scientist",
    "company": "Microsoft",
    "location": "London",
    "skills": ["Python", "Machine Learning", "Data Analysis"],
    "description": "We are looking for a Data Scientist to join our team in London."
  }
]
```

**Annexe 9: Example Candidate Profiles**

```json
[
  {
    "id": 1,
    "nom": "John Doe",
    "email": "john.doe@example.com",
    "compétences": ["Python", "SQL", "Data Analysis"],
    "expérience": 5,
    "localisation": "Paris",
    "secteur": "Data Science"
  },
  {
    "id": 2,
    "nom": "Jane Smith",
    "email": "jane.smith@example.com",
    "compétences": ["Java", "Spring", "SQL"],
    "expérience": 3,
    "localisation": "London",
    "secteur": "Software Engineering"
  }
]
```

**Annexe 10: Project Architecture**

_\[A diagram illustrating the project architecture, including data sources, data flow, databases, API endpoints, and user interface (if any). This could be a Mermaid diagram or a simple flowchart.]_

**Annexe 11: Example Extraction Script**

```python
import requests
from bs4 import BeautifulSoup

def extract_from_web():
    url = "https://realpython.github.io/fake-jobs/"
    scraped_data = []
    try:
        response = requests.get(url)
        response.raise_for_status()
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

**Annexe 12: Example Cleaning Script**

```python
import pandas as pd

def clean_data(df):
    # Convert all text to lowercase
    df = df.apply(lambda x: x.astype(str).str.lower())
    # Remove whitespace
    df = df.apply(lambda x: x.astype(str).str.strip())
    return df
```

**Annexe 13: Swagger Documentation**

_\[A screenshot or a link to the Swagger documentation for the API.]_
