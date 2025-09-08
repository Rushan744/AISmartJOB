# Projet Emploi Matching

Ce projet, "AI SmartJob", est une application complète conçue pour faire correspondre intelligemment les candidats à des opportunités d'emploi. Il utilise des techniques avancées telles que le web scraping, l'intégration d'API externes et l'apprentissage automatique (spécifiquement, un grand modèle linguistique via Ollama) pour des recommandations basées sur l'IA et l'analyse de CV.

## Fonctionnalités Clés

*   **Recommandations d'Emploi Basées sur l'IA :** Recommande les meilleures opportunités d'emploi pour les candidats en fonction de leurs compétences et de leur expérience.
*   **Analyse de CV :** Extrait les compétences clés des CV PDF téléchargés et attribue un score de pertinence à chacune. Il génère également des textes détaillés de recommandation de carrière basés sur le contenu du CV.
*   **Correspondance d'Emploi :** Calcule un score de correspondance entre les emplois individuels et les candidats.
*   **Agrégation de Données :** Collecte des offres d'emploi à partir du web scraping (site exemple) et d'API externes (Adzuna).
*   **Gestion des Utilisateurs :** Inclut une authentification utilisateur de base (connexion, création d'utilisateur).
*   **Système de Feedback :** Permet aux utilisateurs de soumettre des commentaires sur l'application.
*   **Surveillance et Suivi des Expériences :** S'intègre avec Prometheus/Grafana pour la surveillance des performances et MLflow pour le suivi des expériences de modèles d'IA.

## Technologies Utilisées

*   **Backend :** Python (FastAPI, Pandas, PyPDF2, SQLAlchemy, PyMongo, MLflow, Requests, BeautifulSoup4, python-dotenv, passlib)
*   **Frontend :** HTML, CSS (Bootstrap), JavaScript (Plotly pour les visualisations)
*   **Base de Données :** SQLite (pour les données de l'application), MongoDB (pour les données d'emploi Adzuna)
*   **IA/ML :** Ollama (servant le modèle de langage Mistral)
*   **Monitoring :** Prometheus, Grafana
*   **Tests :** Pytest, HTTPX

## Installation et Configuration

Pour démarrer le projet, suivez ces étapes :

### Prérequis

Assurez-vous d'avoir les éléments suivants installés sur votre système :
*   **Python 3.9+**
*   **pip** (gestionnaire de paquets Python)
*   **Docker** et **Docker Compose** (pour MongoDB et la configuration optionnelle d'Ollama)
*   **Ollama :** Téléchargez et installez Ollama depuis [ollama.ai](https://ollama.ai/).

### 1. Cloner le Dépôt

```bash
git clone https://github.com/Rushan744/AISmartJOB.git
cd AISmartJOB/emploi-matching
```

### 2. Installer les Dépendances Python

Naviguez vers le répertoire `emploi-matching` et installez les paquets Python requis :

```bash
pip install -r requirements.txt
```

### 3. Configurer Ollama et Télécharger le Modèle Mistral

Assurez-vous qu'Ollama est en cours d'exécution en arrière-plan. Ensuite, téléchargez le modèle Mistral :

```bash
ollama run mistral
```
(Vous pouvez fermer la session interactive Ollama une fois le modèle téléchargé.)

### 4. Configurer les Variables d'Environnement

Créez un fichier `.env` dans le répertoire `emploi-matching/` avec le contenu suivant. Remplacez les espaces réservés par vos clés/URL réelles.

```dotenv
ADZUNA_API_KEY="VOTRE_CLE_API_ADZUNA" # Obtenez-en une sur developer.adzuna.com
OLLAMA_API_URL="http://localhost:11434/api/generate" # URL par défaut de l'API Ollama
DATABASE_URL="sqlite:///emploi.db" # Ou votre URL de base de données compatible SQLAlchemy préférée
```

### 5. Exécuter MongoDB

Le projet utilise MongoDB pour stocker les données d'emploi Adzuna. Vous pouvez l'exécuter en installant MongoDB localement et en démarrant le service 

### 6. Initialiser les Données

Exécutez le script `main.py` pour générer des données de candidats factices, récupérer les données d'emploi initiales d'Adzuna, scraper des emplois supplémentaires et remplir la base de données SQLite :

```bash
python src/main.py
```
Cette étape effacera et remplira également les tables `jobs` et `candidates` dans `emploi.db`.

## Exécution de l'Application

### 1. Exécuter l'Application Complète avec Docker Compose

Pour une configuration complète incluant le backend FastAPI, Prometheus, Grafana et le frontend, naviguez vers le répertoire `emploi-matching/` et exécutez :

```bash
docker compose up --build -d
```
Cette commande construira les images Docker nécessaires (si elles n'existent pas) et démarrera tous les services en mode détaché.

### 2. Accéder au Frontend

Une fois les services Docker Compose en cours d'exécution, le frontend sera accessible. Ouvrez votre navigateur web et naviguez vers :

```
http://127.0.0.1:8000/
```

Vous serez présenté avec une page de connexion. Vous pouvez utiliser les identifiants par défaut `username: user`, `password: user` ou créer un nouvel utilisateur.

### 3. Exécuter le Backend FastAPI avec Docker

Si vous préférez exécuter uniquement le backend FastAPI via Docker (sans les autres services définis dans `docker-compose.yml`), depuis le répertoire `emploi-matching/`, exécutez :

```bash
docker compose up --build -d emploi-matching-app
```
L'API sera accessible à `http://127.0.0.1:8000`.

## Structure du Projet

*   `src/` : Contient le code source Python principal.
    *   `main.py` : Orchestre la génération, la récupération et la correspondance initiale des données.
    *   `api.py` : Définit tous les points d'API FastAPI (emplois, candidats, correspondances, gestion des utilisateurs, services d'IA, feedback).
    *   `ai_recommender.py` : Logique pour les recommandations d'emploi basées sur l'IA et l'extraction de compétences de CV à l'aide d'Ollama.
    *   `matching.py` : Calcule les scores de correspondance emploi-candidat à l'aide d'Ollama.
    *   `api_jobs.py` : Gère l'intégration avec l'API Adzuna Jobs.
    *   `scraping.py` : Gère le web scraping des données d'emploi à partir d'un site exemple.
    *   `pdf_extractor.py` : Utilitaire pour extraire le contenu textuel des fichiers PDF.
    *   `generate_candidates.py` : Script pour générer des données de candidats synthétiques.
*   `data/` : Stocke les fichiers de données, y compris `candidats.csv`.
*   `frontend/` : Contient l'interface utilisateur web.
    *   `index.html` : La structure HTML principale de l'application frontend.
    *   `script.js` : Logique JavaScript pour l'interactivité du frontend, les appels API et les visualisations Plotly.
*   `monitoring_configs/` : Fichiers de configuration pour les outils de surveillance.
    *   `prometheus.yml` : Configuration Prometheus pour la récupération des métriques de l'application FastAPI.
*   `tests/` : Contient les tests unitaires et d'intégration pour l'application.
    *   `unit/test_api_endpoints.py` : Exemples de tests unitaires pour les points d'API.
    *   `integration/` : Contient les tests d'intégration.
*   `mlruns/` : Répertoire utilisé par MLflow pour stocker les données de suivi des expériences.
*   `mlartifacts/` : Répertoire utilisé par MLflow pour stocker les artefacts des exécutions.
*   `docker-compose.yml` : Fichier Docker Compose pour la configuration des services Docker (application, Prometheus, Grafana).
*   `requirements.txt` : Liste toutes les dépendances Python.
*   `.env.example` : Un modèle pour le fichier des variables d'environnement.
*   `__init__.py` : Fichier d'initialisation du package Python.
*   `.gitignore` : Fichier de configuration Git pour ignorer les fichiers non suivis.
*   `emploi.db` : Base de données SQLite utilisée par l'application.
*   `build_and_run.ps1` / `build_and_run.sh` : Scripts pour la construction et l'exécution de l'application (PowerShell et Bash).

## Surveillance et Suivi des Expériences

*   **Prometheus & Grafana :** L'application FastAPI est instrumentée avec des métriques Prometheus. Vous pouvez configurer Prometheus pour récupérer ces métriques et Grafana pour les visualiser.
    *   Des exemples de tableaux de bord Grafana sont affichés dans `screenshot/grafana_promethuese_monitoring.png` et `screenshot/erreur pendant le telecharge le cv_grafana.png`.
    *   Des alertes peuvent être configurées, comme on le voit dans `screenshot/Alert message au Discord_monitoring.png`.
*   **MLflow :** MLflow est intégré pour suivre les expériences, en particulier pour le point d'API `extract_skills_from_cv`. Cela permet d'enregistrer les paramètres, les métriques et les artefacts liés à l'analyse de CV.
    *   L'interface utilisateur MLflow peut être consultée (par exemple, `mlflow ui`) pour visualiser les exécutions d'expériences, comme démontré dans `screenshot/MLflow.png`.

## Tests

Le projet comprend des tests pour assurer la fonctionnalité et la fiabilité.

Pour exécuter les tests unitaires :

```bash
pytest emploi-matching/tests/unit/
```
*   Les exemples de résultats de tests sont affichés dans `screenshot/test unitaire.png`.
*   Les tests d'intégration peuvent être effectués à l'aide d'outils comme Postman (`screenshot/postman_test_integration_API.png`) ou Katalon (`screenshot/Katalon_test_integration_Appli.png`).

## CI/CD (Intégration et Déploiement Continus)

Le projet utilise **GitHub Actions** pour l'intégration continue. Des workflows automatisés sont configurés pour garantir la qualité du code et la fiabilité de l'application.

*   **Tests Python :** Un workflow nommé "Python Tests" est configuré pour exécuter automatiquement les tests unitaires et d'intégration à chaque push. Cela permet de détecter rapidement les régressions et les problèmes de code.
*   Vous pouvez consulter l'état et l'historique des exécutions de ces workflows sur la page "Actions" de votre dépôt GitHub.

## Contribution

N'hésitez pas à contribuer à ce projet en soumettant des pull requests.

## Licence

[MIT](LICENSE)
