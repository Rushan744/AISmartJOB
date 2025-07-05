Mise en situation 1 (E1)

Collecte, stockage et mise à disposition des données d’un projet IA

Projet IA: SmartJob - Application de mise en relation emploi-candidat

Formation Développeur en Intelligence Artificielle
RNCP 37827
Promotion 2023-2024

RUSHAN ZAMIR Saeedullah

SOMMAIRE

Introduction 3
Présentation du projet 3
Contexte du projet 3
Spécifications techniques 3
Extraction des données 4
Données issues d’un service web (API) 4
Données issues d’une page web 4
Données issues d’un fichier 4
Données issues d’un base de données relationnelles 4
Données issues d’un système big data 4
Requêtage des données 5
Requêtes de type SQL 5
Requêtes depuis un système big data 5
Agrégation des données 5
Préparation des données 5
Agrégation des données 5
Jeu de données final 5
Création de la base de données 6
Modélisation des données 6
Modèle physique des données (MPD) 6
Choix du système de gestion de la base données (SGBD) 6
Création de la base de données 6
Import des données 6
Conformité RGPD 6
Développement de l’API 7
Spécifications fonctionnelles et techniques 7
Conception de l’architecture de l’API 7
Documentation 7
Perspectives et améliorations 7
Conclusions 7
Annexes 8

---

**Note : il est attendu un rapport de 2 à 5 pages pour ce livrable**

### 1. Introduction

#### Présentation du projet
L'application **SmartJob** vise à mettre en relation les demandeurs d'emploi avec des offres d'emploi pertinentes. Elle agrège les offres d'emploi provenant de diverses sources, notamment une API publique et des analyses web, et les met en relation avec les profils de candidats en fonction de leurs compétences, de leur expérience et de leur localisation. L'application permet de mettre efficacement en relation les candidats et les offres d'emploi grâce à un système de notation.

#### Contexte du projet
Ce projet s'inscrit dans le cadre d'un programme de formation destiné aux développeurs. Son objectif est de démontrer la capacité à collecter, stocker et traiter des données pour une application data-driven. Il simule un scénario réel où les demandeurs d'emploi et les employeurs peuvent se rencontrer grâce à un processus de mise en relation automatisé.

#### Spécifications techniques
Le projet est principalement développé en **Python** pour l'ensemble des processus d'extraction, de traitement des données et de développement de l'API. Les principales bibliothèques et outils utilisés incluent :
*   `requests` : Pour les interactions avec les APIs REST et le web scraping.
*   `BeautifulSoup4` : Pour l'analyse et l'extraction de données à partir de pages web HTML.
*   `pandas` : Pour la manipulation et la transformation des jeux de données.
*   `SQLAlchemy` : Utilisé comme ORM (Object-Relational Mapper) pour interagir avec la base de données SQLite.
*   `FastAPI` : Un framework web moderne et performant pour la construction de l'API RESTful, offrant validation automatique des données et documentation interactive.
*   `PyMongo` : Pour la connexion et l'interaction avec la base de données MongoDB.
*   `Faker` : Pour la génération de données de candidats factices à des fins de test et de développement.
*   `PyPDF2` : Pour l'extraction de texte à partir de fichiers PDF (utilisé pour l'analyse des CV).
*   `passlib[bcrypt]` : Pour le hachage sécurisé des mots de passe des utilisateurs.

L'application utilise deux systèmes de gestion de base de données :
*   **SQLite** : Pour le stockage local des données structurées et relationnelles (profils de candidats, offres d'emploi normalisées, et résultats de correspondance).
*   **MongoDB** : Pour le stockage initial des données brutes et potentiellement non structurées des offres d'emploi récupérées via l'API Adzuna.

Le flux de données consiste à extraire les données d'emploi de l'API Adzuna et de sources web, combinées, normalisées, puis stockées dans SQLite. Les données des candidats sont chargées à partir d'un fichier CSV. L'application associe ensuite les offres d'emploi aux candidats selon des critères prédéfinis et stocke les résultats. L'accès à l'API est sécurisé par une authentification HTTP de base.

**Schéma global du flux de données:**

```mermaid
graph TD
    A[Adzuna API] --> B(Scraping Module);
    B --> C{Raw Job Data};
    C --> D[MongoDB (adzuna_jobs)];
    E[Web Scraping Source] --> B;
    F[candidats.csv] --> G(Candidate Data Loading);
    D -- Processed Job Data --> H(Data Normalization & Aggregation);
    H --> I[SQLite DB (jobs table)];
    G --> J[SQLite DB (candidates table)];
    I & J --> K(Matching & Processing Module);
    K -- Job Recommendations & Career Text --> L[Frontend (index.html)];
    K -- Extracted Skills --> L;
    L -- CV Upload --> K;
    L -- User Login --> M(FastAPI Backend - Authentication);
    M --> N[SQLite DB (users table - implied)];
    K -- Match Scores --> O[SQLite DB (matches table)];
```

### 2. Extraction des données

Le projet met en œuvre des scripts d'extraction pour collecter des données à partir de diverses sources, garantissant la pérennité de la collecte nécessaire au projet.

#### Données issues d’un service web (API)
Les offres d'emploi sont récupérées de l'**API Adzuna**. L'application envoie des requêtes HTTP GET à l'API avec des paramètres de recherche spécifiques (ex: `what='developer'`, `where='Paris'`). La réponse est un objet JSON structuré contenant des champs comme `title`, `company`, `location` (qui peut être un objet imbriqué), `description`, etc. Ces données brutes sont initialement stockées dans une collection dédiée de **MongoDB** (`adzuna_jobs`) pour une ingestion rapide et flexible.
*Exemple de données brutes Adzuna (simplifié) :*
```json
{
  "title": "Développeur Fullstack",
  "company": {"display_name": "Tech Solutions"},
  "location": {"display_name": "Paris"},
  "description": "Développement d'applications web..."
}
```

#### Données issues d’une page web
Des offres d'emploi sont également extraites par web scraping à partir d'une URL prédéfinie, comme le site "Real Python Fake Jobs". Le script utilise `requests` pour obtenir le contenu HTML de la page et `BeautifulSoup4` pour analyser ce contenu. Il cible des éléments HTML spécifiques (ex: balises `<h2>` pour les titres de poste, `<h3>` pour les entreprises) pour extraire les informations pertinentes. Ces données sont ensuite combinées avec celles de l'API Adzuna.
*Exemple de données extraites par scraping (simplifié) :*
```
{
  "title": "Ingénieur Logiciel",
  "company": "Innovate Corp",
  "location": "Lyon",
  "description": "Conception et implémentation de systèmes logiciels."
}
```
La différence fondamentale entre les données extraites via API et web scraping réside dans leur **source et leur structure initiale**. L'API Adzuna fournit des données déjà structurées en format JSON, ce qui facilite leur ingestion directe. En revanche, le web scraping implique l'extraction de données à partir de pages HTML non structurées, nécessitant une analyse syntaxique (parsing) pour identifier et extraire les informations pertinentes. Bien que les deux sources fournissent des offres d'emploi, la méthode de collecte et le format initial des données diffèrent significativement.

#### Données issues d’un fichier
Les données des candidats sont chargées à partir d'un fichier CSV nommé `candidats.csv`. Ce fichier contient des informations structurées sur les profils des demandeurs d'emploi, telles que leur nom, email, compétences, années d'expérience, localisation et secteur d'activité. La bibliothèque `pandas` est utilisée pour lire et manipuler ces données.
*Exemple de ligne dans `candidats.csv` :*
`id,nom,email,compétences,expérience,localisation,secteur`
`1,Alice Dupont,alice@example.com,"Python, SQL, Analyse de données",5,Paris,IT`

#### Données issues d’un base de données relationnelles
Dans le contexte de l'extraction initiale, la base de données relationnelle (SQLite) n'est pas une source d'extraction primaire. Elle est la destination finale pour les données d'emploi et de candidat après leur agrégation et normalisation. Cependant, des requêtes sont effectuées sur cette base pour récupérer les données nécessaires au processus de correspondance et à l'exposition via l'API.

#### Données issues d’un système big data
Le projet utilise **MongoDB** comme système de stockage pour les données brutes issues de l'API Adzuna. Bien que MongoDB soit une base de données NoSQL capable de gérer de grands volumes de données non structurées, son rôle ici est principalement celui d'un point d'ingestion initial. Les données y sont stockées telles quelles, puis des processus ultérieurs les extraient, les transforment et les normalisent pour les intégrer dans la base de données relationnelle SQLite, qui est le cœur du système de correspondance. Ainsi, MongoDB est alimenté par l'API Adzuna, et ses données sont ensuite consommées pour enrichir la base SQLite. La base MongoDB est donc utilisée comme un "staging area" ou un cache pour les données brutes avant leur traitement et leur intégration dans le modèle relationnel.

### 3. Requêtage des données

Le requêtage des données s'effectue principalement à partir des bases de données développées pour les besoins du projet, afin de préparer les données nécessaires aux processus de correspondance et d'analyse.

#### Requêtes de type SQL
L'application interagit avec la base de données **SQLite** via **SQLAlchemy**. Des requêtes SQL (générées par l'ORM) sont utilisées pour :
*   **Récupération :** Lire les profils de candidats (`SELECT * FROM candidates`), les offres d'emploi normalisées (`SELECT * FROM jobs`), et les correspondances existantes (`SELECT * FROM matches`).
    *   *Objectif :* Fournir les données nécessaires au module de correspondance et aux points de terminaison de l'API.
    *   *Résultat :* Des listes d'objets Python représentant les enregistrements des tables, facilement manipulables.
*   **Insertion :** Ajouter de nouvelles offres d'emploi et de nouveaux candidats après l'extraction et la préparation.
*   **Mise à jour/Suppression :** Gérer le cycle de vie des données (ex: `DELETE FROM jobs` avant une nouvelle insertion massive pour rafraîchir les données).

#### Requêtes depuis un système big data
Des requêtes sont effectuées sur la base de données **MongoDB** pour récupérer les données brutes des offres d'emploi stockées dans la collection `adzuna_jobs`.
*   *Objectif :* Accéder aux informations non structurées ou semi-structurées directement issues de l'API Adzuna avant qu'elles ne soient normalisées et transférées vers la base de données SQLite pour l'intégration dans le processus de correspondance.
*   *Résultat :* Des documents JSON bruts, qui sont ensuite traités pour extraction et normalisation.

### 4. Agrégation des données

L'agrégation des données est un processus crucial qui combine les informations provenant de différentes sources et les prépare pour le stockage et l'utilisation dans le système de correspondance.

#### Préparation des données
La préparation des données implique le nettoyage et la transformation des données extraites afin d'en garantir la cohérence et l'exactitude. Cela comprend :
*   **Gestion des valeurs manquantes :** L'application gère les valeurs manquantes en fournissant des valeurs par défaut (ex: chaîne vide pour une description manquante) ou en ignorant les entrées incomplètes, selon la criticité du champ.
*   **Homogénéisation des formats de données :** Les données sont normalisées pour assurer l'uniformité. Par exemple, les chaînes de caractères sont converties en minuscules et les espaces superflus sont supprimés (`.strip()`). Les structures de localisation complexes (objets JSON de l'API Adzuna) sont aplaties en simples chaînes de caractères.
    *   *Exemple d'homogénéisation de localisation :* Si l'API Adzuna renvoie `{"location": {"display_name": "Paris"}}`, cela est transformé en `"Paris"`. Si le scraping renvoie directement `"Paris"`, le format est déjà compatible.

#### Agrégation des données
Les données des offres d'emploi issues de l'API Adzuna (après récupération de MongoDB) et celles provenant du web scraping sont combinées en un seul ensemble de données. Ce processus implique la normalisation des structures de données et la gestion des éventuelles incohérences entre les sources. L'objectif est de créer un jeu de données unique et cohérent qui servira d'entrée pour le système de correspondance.
*Exemple d'agrégation :*
Les champs `title`, `company`, `location`, `description` sont extraits de chaque source. Si l'API Adzuna utilise `company.display_name` et le scraping utilise `company_name`, ces champs sont mappés à un champ `company` unique dans le jeu de données agrégé. Les données sont ensuite fusionnées dans une liste unique d'objets emploi.

#### Jeu de données final
Le jeu de données final est le résultat de l'agrégation et de la préparation des données. Il s'agit d'un ensemble de données unifié, nettoyé et normalisé, prêt à être importé dans la base de données SQLite pour le stockage et à être utilisé par le module de correspondance. Ce jeu de données est la source unique de vérité pour les offres d'emploi dans le processus de matching.

### 5. Création de la base de données

L'application utilise deux systèmes de gestion de base de données pour répondre à des besoins différents : SQLite pour les données structurées et MongoDB pour les données brutes et flexibles.

#### Modélisation des données
La modélisation des données a été réalisée en utilisant la **méthode Merise**, une approche structurée pour la conception de systèmes d'information. Elle se décompose en trois niveaux :
1.  **Modèle Conceptuel des Données (MCD) :** Décrit les données du point de vue de l'utilisateur, sans contraintes techniques. Il identifie les entités (objets du monde réel) et les relations entre elles. Pour SmartJob, les entités principales sont `Candidat`, `Emploi`, et `Correspondance`.
2.  **Modèle Logique des Données (MLD) :** Traduit le MCD en une structure compatible avec un SGBD relationnel, en définissant les tables, les attributs (colonnes) et les clés primaires/étrangères.
3.  **Modèle Physique des Données (MPD) :** Spécifie l'implémentation concrète du MLD dans un SGBD donné, incluant les types de données spécifiques, les contraintes d'intégrité, et les index.

La méthode Merise a été mise en œuvre en partant d'une analyse des besoins fonctionnels (mettre en relation candidats et emplois) pour identifier les entités et leurs propriétés. Par exemple, un "Candidat" a un nom, des compétences, etc. Les relations ont ensuite été définies (un Candidat peut correspondre à plusieurs Emplois, un Emploi peut correspondre à plusieurs Candidats, d'où une table de liaison "Correspondance"). Le passage au MLD a permis de définir les tables et leurs colonnes, et enfin le MPD a concrétisé cela pour SQLite.

#### Modèle physique des données (MPD)
Le modèle physique des données est implémenté à l'aide de **SQLite** et géré par **SQLAlchemy**. Les tables ont été conçues pour représenter les entités clés du projet et leurs relations, garantissant l'intégrité et l'efficacité des requêtes.

*   **`candidates` :** Stocke les informations sur les demandeurs d'emploi.
    *   `id` (INTEGER PRIMARY KEY) : Identifiant unique pour chaque candidat. C'est une clé primaire pour garantir l'unicité et permettre des références rapides.
    *   `nom` (TEXT) : Nom complet du candidat.
    *   `email` (TEXT) : Adresse email du candidat.
    *   `compétences` (TEXT) : Compétences du candidat, stockées sous forme de chaîne de caractères (ex: "Python, SQL, Analyse de données").
    *   `expérience` (INTEGER) : Années d'expérience professionnelle du candidat.
    *   `localisation` (TEXT) : Ville de résidence du candidat.
    *   `secteur` (TEXT) : Secteur d'activité dans lequel le candidat recherche un emploi.
    *   *Justification :* Cette table regroupe toutes les informations essentielles pour identifier un candidat et évaluer sa pertinence pour un poste. Les champs ont été choisis pour capturer les attributs clés d'un profil professionnel.

*   **`jobs` :** Stocke les informations normalisées sur les offres d'emploi.
    *   `id` (INTEGER PRIMARY KEY) : Identifiant unique pour chaque offre d'emploi.
    *   `title` (TEXT) : Titre de l'offre d'emploi.
    *   `company` (TEXT) : Nom de l'entreprise proposant l'emploi.
    *   `location` (TEXT) : Lieu géographique de l'emploi.
    *   `description` (TEXT) : Description détaillée de l'offre d'emploi.
    *   *Justification :* Cette table contient les informations clés des postes, agrégées et normalisées à partir de différentes sources, prêtes pour le matching. Les champs sont standardisés pour faciliter les comparaisons.

*   **`matches` :** Stocke les résultats des correspondances entre candidats et emplois.
    *   `id` (INTEGER PRIMARY KEY) : Identifiant unique pour chaque correspondance.
    *   `job_id` (INTEGER FOREIGN KEY) : Clé étrangère faisant référence à l'`id` de la table `jobs`. Elle établit un lien direct avec l'offre d'emploi concernée.
    *   `candidate_id` (INTEGER FOREIGN KEY) : Clé étrangère faisant référence à l'`id` de la table `candidates`. Elle établit un lien direct avec le candidat concerné.
    *   `score` (INTEGER) : Score numérique (entre 0 et 100) représentant la qualité de la correspondance.
    *   *Justification :* Cette table est essentielle pour stocker les résultats du processus de matching, permettant de retrouver rapidement les emplois les plus pertinents pour un candidat ou vice-versa. Les clés étrangères garantissent l'intégrité référentielle et l'efficacité des jointures entre les tables `jobs` et `candidates`.

*   **`users` :** Stocke les informations d'authentification des utilisateurs.
    *   `id` (INTEGER PRIMARY KEY) : Identifiant unique de l'utilisateur.
    *   `username` (TEXT UNIQUE) : Nom d'utilisateur unique.
    *   `hashed_password` (TEXT) : Mot de passe haché de l'utilisateur.
    *   *Justification :* Cette table est essentielle pour la gestion des accès et la sécurisation de l'API, permettant l'authentification des utilisateurs avant qu'ils n'accèdent aux fonctionnalités du système.

#### Choix du système de gestion de la base données (SGBD)
*   **SQLite :** A été choisi pour sa simplicité, sa légèreté et sa facilité d'utilisation. Il est idéal pour le stockage local des données structurées du projet et ne nécessite pas de serveur de base de données distinct, ce qui simplifie le déploiement et la gestion pour un projet de cette envergure. Son adéquation réside dans sa capacité à gérer des données relationnelles avec des transactions ACID, parfait pour les données de candidats, d'emplois normalisés et de correspondances qui ont une structure fixe et des relations claires.
*   **MongoDB :** A été choisi pour stocker les données brutes des offres d'emploi récupérées depuis l'API Adzuna. En tant que base de données NoSQL orientée document, MongoDB est particulièrement adaptée à l'ingestion de données semi-structurées ou non structurées, comme les réponses JSON complexes des APIs externes. Sa flexibilité permet de stocker les données telles quelles avant toute transformation, ce qui est un avantage pour la phase de collecte et d'ingestion de données hétérogènes.

#### Création de la base de données
La base de données SQLite (`emploi.db`) est créée programmatiquement au démarrage de l'application via SQLAlchemy. L'application définit les schémas des tables (`UserDB`, `JobDB`, `CandidateDB`, `MatchDB`) et utilise `Base.metadata.create_all(engine)` pour générer ces tables si elles n'existent pas. Ce processus est automatisé par le script `main.py`.

#### Import des données
L'alimentation de la base de données est réalisée par des scripts Python.
*   Les données des candidats sont importées à partir du fichier `candidats.csv` en utilisant `pandas`, puis insérées dans la table `candidates` de SQLite.
*   Les données d'emploi, après avoir été extraites de l'API Adzuna (et potentiellement stockées temporairement dans MongoDB) et du web scraping, sont agrégées, normalisées, puis insérées dans la table `jobs` de SQLite. Ce processus assure que la base de données relationnelle contient un jeu de données propre et cohérent pour le matching.

### 6. Conformité RGPD

Le projet SmartJob traite des données personnelles (nom, email, compétences, expérience, localisation) des candidats, ce qui implique des exigences de conformité au Règlement Général sur la Protection des Données (RGPD). La sécurisation des points de terminaison de l'API avec authentification est une mesure clé, et d'autres aspects sont également pris en compte :

*   **Finalité du traitement :** Les données personnelles sont collectées et traitées dans le but exclusif de mettre en relation les candidats avec des offres d'emploi pertinentes et de fournir des recommandations de carrière. Cette finalité est clairement définie et communiquée.
*   **Minimisation des données :** Seules les données strictement nécessaires à la réalisation de la finalité du projet sont collectées et stockées. Les champs sont limités aux informations pertinentes pour le matching et la recommandation.
*   **Base légale du traitement :** Le traitement des données est basé sur le consentement de l'utilisateur (implicite lors de l'upload du CV ou de la création de compte) et l'exécution d'un contrat (fourniture du service de matching). Il est recommandé d'ajouter une acceptation explicite des conditions d'utilisation et de la politique de confidentialité.
*   **Durée de stockage :** Les données personnelles sont conservées uniquement pendant la durée nécessaire à la réalisation de la finalité du traitement. Une politique de rétention des données devrait être définie, par exemple, la suppression des données après une période d'inactivité du compte (ex: 2 ans) ou sur demande explicite de l'utilisateur.
*   **Sécurisation des données :**
    *   **Authentification :** L'API utilise l'authentification HTTP Basic avec des mots de passe hachés (`passlib[bcrypt]`) pour protéger l'accès aux données sensibles. Seuls les utilisateurs authentifiés peuvent accéder à leurs propres données ou aux données publiques (offres d'emploi).
    *   **Contrôle d'accès :** Les points de terminaison de l'API sont protégés, et l'accès aux données utilisateurs est restreint aux utilisateurs authentifiés. Un utilisateur "admin" a des privilèges pour voir tous les utilisateurs, ce qui nécessite une gestion rigoureuse de ce compte et de ses accès.
    *   **Intégrité :** En contrôlant l'accès, le risque de modifications ou de suppressions non autorisées des données est minimisé.
*   **Droits des personnes concernées :** Bien que non implémenté dans l'interface actuelle, le système doit prévoir la possibilité pour les utilisateurs d'exercer leurs droits RGPD :
    *   **Droit d'accès :** Obtenir la confirmation que leurs données sont traitées et y accéder.
    *   **Droit de rectification :** Demander la correction de données inexactes.
    *   **Droit à l'effacement ("droit à l'oubli") :** Demander la suppression de leurs données.
    *   **Droit à la limitation du traitement :** Demander la suspension du traitement de leurs données.
    *   **Droit d'opposition :** S'opposer au traitement de leurs données.
    *   **Droit à la portabilité :** Recevoir leurs données dans un format structuré et couramment utilisé.

### 7. Développement de l’API

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
