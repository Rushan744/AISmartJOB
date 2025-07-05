import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.declarative import declarative_base # Import declarative_base

# Import the FastAPI app and database models from your api.py
from src.api import app, get_db, UserDB, JobDB, CandidateDB, MatchDB, get_password_hash, verify_password, get_user, get_current_user
from src.api import Job, Candidate, Match, SkillScore, SkillsExtractionResponse, UserCreate, User, CVRecommendationResponse
from src.api import Base # Import Base for metadata operations

# Mock the database engine and session for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Use a mock session for dependency override
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()

# Helper fixtures for mock users
@pytest.fixture
def test_user_mock():
    return UserDB(id=1, username="testuser", hashed_password=get_password_hash("testpassword"))

@pytest.fixture
def admin_user_mock():
    return UserDB(id=2, username="admin", hashed_password=get_password_hash("adminpassword"))

# Mock AI recommender and PDF extractor functions
@pytest.fixture
def mock_ai_recommender():
    with patch("src.api.get_ai_recommendations") as mock_get_ai_recs, \
         patch("src.api.get_ai_recommendations_from_cv") as mock_get_ai_recs_cv, \
         patch("src.api.extract_skills_with_scores_from_cv") as mock_extract_skills:
        yield mock_get_ai_recs, mock_get_ai_recs_cv, mock_extract_skills

@pytest.fixture
def mock_pdf_extractor():
    with patch("src.api.extract_text_from_pdf") as mock_extract_text:
        yield mock_extract_text

# Test for User Management Endpoints
def test_create_user(client: TestClient, db_session: Session):
    response = client.post(
        "/users/",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

    # Verify user is in DB
    user_in_db = db_session.query(UserDB).filter(UserDB.username == "testuser").first()
    assert user_in_db is not None
    assert verify_password("testpassword", user_in_db.hashed_password)

def test_create_user_existing_username(client: TestClient, db_session: Session):
    # Create a user first
    hashed_password = get_password_hash("existingpass")
    db_session.add(UserDB(username="existinguser", hashed_password=hashed_password))
    db_session.commit()

    response = client.post(
        "/users/",
        json={"username": "existinguser", "password": "newpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

# Test for ETL Endpoints
@pytest.fixture
def mock_current_user():
    return UserDB(id=1, username="testuser", hashed_password="hashedpassword")

def test_read_jobs(client: TestClient, db_session: Session, mock_current_user: UserDB):
    # Add some test jobs
    job1 = JobDB(id=1, title="Dev", company="CompA", location="LocA", description="DescA")
    job2 = JobDB(id=2, title="QA", company="CompB", location="LocB", description="DescB")
    db_session.add_all([job1, job2])
    db_session.commit()

    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.get("/jobs/")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) == 2
    assert jobs[0]["title"] == "Dev"
    assert jobs[1]["title"] == "QA"

    # # Clear the override after the test
    # app.dependency_overrides.clear()
    # # Add some test jobs
    # job1 = JobDB(id=1, title="Dev", company="CompA", location="LocA", description="DescA")
    # job2 = JobDB(id=2, title="QA", company="CompB", location="LocB", description="DescB")
    # db_session.add_all([job1, job2])
    # db_session.commit()

    # response = client.get("/jobs/")
    # assert response.status_code == 200
    # jobs = response.json()
    # assert len(jobs) == 2
    # assert jobs[0]["title"] == "Dev"
    # assert jobs[1]["title"] == "QA"

def test_read_candidates(client: TestClient, db_session: Session, mock_current_user: UserDB):
    # Add some test candidates
    candidate1 = CandidateDB(id=1, nom="CandA", email="a@b.com", compétences="Python", expérience=3, localisation="Paris", secteur="IT")
    candidate2 = CandidateDB(id=2, nom="CandB", email="c@d.com", compétences="Java", expérience=5, localisation="Lyon", secteur="IT")
    db_session.add_all([candidate1, candidate2])
    db_session.commit()

    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.get("/candidates/")
    assert response.status_code == 200
    candidates = response.json()
    assert len(candidates) == 2
    assert candidates[0]["nom"] == "CandA"
    assert candidates[1]["nom"] == "CandB"

    # # Clear the override after the test
    # app.dependency_overrides.clear()
    # # Add some test candidates
    # candidate1 = CandidateDB(id=1, nom="CandA", email="a@b.com", compétences="Python", expérience=3, localisation="Paris", secteur="IT")
    # candidate2 = CandidateDB(id=2, nom="CandB", email="c@d.com", compétences="Java", expérience=5, localisation="Lyon", secteur="IT")
    # db_session.add_all([candidate1, candidate2])
    # db_session.commit()

    # response = client.get("/candidates/")
    # assert response.status_code == 200
    # candidates = response.json()
    # assert len(candidates) == 2
    # assert candidates[0]["nom"] == "CandA"
    # assert candidates[1]["nom"] == "CandB"

def test_read_matches(client: TestClient, db_session: Session, mock_current_user: UserDB):
    # Add some test jobs and candidates for matches
    job1 = JobDB(id=1, title="Dev", company="CompA", location="LocA", description="DescA")
    candidate1 = CandidateDB(id=1, nom="CandA", email="a@b.com", compétences="Python", expérience=3, localisation="Paris", secteur="IT")
    db_session.add_all([job1, candidate1])
    db_session.commit()

    match1 = MatchDB(id=1, job_id=job1.id, candidate_id=candidate1.id, score=90)
    db_session.add(match1)
    db_session.commit()

    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.get("/matches/")
    assert response.status_code == 200
    matches = response.json()
    assert len(matches) == 1
    assert matches[0]["job_id"] == 1
    assert matches[0]["candidate_id"] == 1
    assert matches[0]["score"] == 90.0

    # # Clear the override after the test
    # app.dependency_overrides.clear()
    # # Add some test jobs and candidates for matches
    # job1 = JobDB(id=1, title="Dev", company="CompA", location="LocA", description="DescA")
    # candidate1 = CandidateDB(id=1, nom="CandA", email="a@b.com", compétences="Python", expérience=3, localisation="Paris", secteur="IT")
    # db_session.add_all([job1, candidate1])
    # db_session.commit()

    # match1 = MatchDB(id=1, job_id=job1.id, candidate_id=candidate1.id, score=90)
    # db_session.add(match1)
    # db_session.commit()

    # response = client.get("/matches/")
    # assert response.status_code == 200
    # matches = response.json()
    # assert len(matches) == 1
    # assert matches[0]["job_id"] == 1
    # assert matches[0]["candidate_id"] == 1
    # assert matches[0]["score"] == 90.0

# Test for AI SmartJob Endpoints
def test_get_recommendations_for_candidate(client: TestClient, db_session: Session, mock_current_user: UserDB, mock_ai_recommender):
    mock_get_ai_recs, _, _ = mock_ai_recommender

    # Add a candidate and jobs
    candidate1 = CandidateDB(id=1, nom="CandA", email="a@b.com", compétences="Python", expérience=3, localisation="Paris", secteur="IT")
    job1 = JobDB(id=1, title="Dev", company="CompA", location="LocA", description="DescA")
    job2 = JobDB(id=2, title="QA", company="CompB", location="LocB", description="DescB")
    db_session.add_all([candidate1, job1, job2])
    db_session.commit()

    # Configure the mock AI recommender
    mock_get_ai_recs.return_value = [
        {"id": 1, "title": "Dev", "company": "CompA", "location": "LocA", "description": "DescA"}
    ]

    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.get("/ai_smartjob/recommendations/CandA")
    assert response.status_code == 200
    recommendations = response.json()
    assert len(recommendations) == 1
    assert recommendations[0]["title"] == "Dev"
    mock_get_ai_recs.assert_called_once()

    # Clear the override after the test
    app.dependency_overrides.clear()

# def test_get_recommendations_for_candidate_not_found(client: TestClient, mock_current_user: UserDB):
#     # Override get_current_user for this test
#     app.dependency_overrides[get_current_user] = lambda: mock_current_user

#     response = client.get("/ai_smartjob/recommendations/NonExistentCand")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Candidat 'NonExistentCand' non trouvé"

#     # Clear the override after the test
#     app.dependency_overrides.clear()
#     response = client.get("/ai_smartjob/recommendations/NonExistentCand")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Candidat 'NonExistentCand' non trouvé"

def test_recommend_jobs_from_cv(client: TestClient, db_session: Session, mock_current_user: UserDB, mock_ai_recommender, mock_pdf_extractor):
    _, mock_get_ai_recs_cv, _ = mock_ai_recommender
    mock_extract_text = mock_pdf_extractor

    # Add some jobs
    job1 = JobDB(id=1, title="Dev", company="CompA", location="LocA", description="DescA")
    db_session.add(job1)
    db_session.commit()

    # Mock PDF extraction and AI recommendations
    mock_extract_text.return_value = "Sample CV text"
    mock_get_ai_recs_cv.return_value = ([{"id": 1, "title": "Dev", "company": "CompA", "location": "LocA", "description": "DescA"}], "Career advice text")

    # Create a dummy PDF file in memory
    dummy_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Parent 2 0 R>>endobj 4 0 obj<</Length 11>>stream\nBT/F1 12 Tf 72 712 Td (Hello) TjET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000110 00000 n\n0000000200 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n221\n%%EOF"

    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.post(
        "/ai_smartjob/recommend_from_cv/",
        files={"fichier_cv": ("test.pdf", dummy_pdf_content, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommended_jobs"]) == 1
    assert data["recommended_jobs"][0]["title"] == "Dev"
    assert data["career_recommendation_text"] == "Career advice text"
    mock_extract_text.assert_called_once_with(dummy_pdf_content)
    mock_get_ai_recs_cv.assert_called_once_with("Sample CV text", [{"id": 1, "title": "Dev", "company": "CompA", "location": "LocA", "description": "DescA"}])

    # Clear the override after the test
    app.dependency_overrides.clear()

def test_recommend_jobs_from_cv_invalid_file_type(client: TestClient, mock_current_user: UserDB):
    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.post(
        "/ai_smartjob/recommend_from_cv/",
        files={"fichier_cv": ("test.txt", b"some text", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Seuls les fichiers PDF sont supportés."

    # # Clear the override after the test
    # app.dependency_overrides.clear()
    # response = client.post(
    #     "/ai_smartjob/recommend_from_cv/",
    #     files={"fichier_cv": ("test.txt", b"some text", "text/plain")}
    # )
    # assert response.status_code == 400
    # assert response.json()["detail"] == "Seuls les fichiers PDF sont supportés."

def test_recommend_jobs_from_cv_empty_pdf(client: TestClient, mock_current_user: UserDB, mock_pdf_extractor):
    mock_extract_text = mock_pdf_extractor
    mock_extract_text.return_value = "" # Simulate empty text extraction

    dummy_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Parent 2 0 R>>endobj 4 0 obj<</Length 11>>stream\nBT/F1 12 Tf 72 712 Td (Hello) TjET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000110 00000 n\n0000000200 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n221\n%%EOF"

    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.post(
        "/ai_smartjob/recommend_from_cv/",
        files={"fichier_cv": ("empty.pdf", dummy_pdf_content, "application/pdf")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Impossible d'extraire le texte du PDF. Le PDF pourrait être vide ou basé sur des images."

    # # Clear the override after the test
    # app.dependency_overrides.clear()
    # mock_extract_text = mock_pdf_extractor
    # mock_extract_text.return_value = "" # Simulate empty text extraction

    # dummy_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Parent 2 0 R>>endobj 4 0 obj<</Length 11>>stream\nBT/F1 12 Tf 72 712 Td (Hello) TjET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000110 00000 n\n0000000200 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n221\n%%EOF"

    # response = client.post(
    #     "/ai_smartjob/recommend_from_cv/",
    #     files={"fichier_cv": ("empty.pdf", dummy_pdf_content, "application/pdf")}
    # )
    # assert response.status_code == 400
    # assert response.json()["detail"] == "Impossible d'extraire le texte du PDF. Le PDF pourrait être vide ou basé sur des images."

def test_read_root(client: TestClient):
    # Mock the open function to simulate reading index.html
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_file = MagicMock()
        mock_file.read.return_value = "<html><body><h1>Hello Frontend!</h1></body></html>"
        mock_open.return_value.__enter__.return_value = mock_file

        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert "Hello Frontend!" in response.text
        mock_open.assert_called_once_with("frontend/index.html", "r", encoding="utf-8")

def test_extract_skills_from_cv_endpoint(client: TestClient, mock_current_user: UserDB, mock_ai_recommender, mock_pdf_extractor):
    _, _, mock_extract_skills = mock_ai_recommender
    mock_extract_text = mock_pdf_extractor

    # Mock PDF extraction and AI skill extraction
    mock_extract_text.return_value = "Sample CV text with skills"
    mock_extract_skills.return_value = [
        {"skill": "Python", "score": 90},
        {"skill": "SQL", "score": 75}
    ]

    dummy_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Parent 2 0 R>>endobj 4 0 obj<</Length 11>>stream\nBT/F1 12 Tf 72 712 Td (Hello) TjET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000110 00000 n\n0000000200 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n221\n%%EOF"

    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.post(
        "/ai_smartjob/extract_skills_from_cv/",
        files={"fichier_cv": ("test_skills.pdf", dummy_pdf_content, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["extracted_skills"]) == 2
    assert data["extracted_skills"][0]["skill"] == "Python"
    assert data["extracted_skills"][0]["score"] == 90
    mock_extract_text.assert_called_once_with(dummy_pdf_content)
    mock_extract_skills.assert_called_once_with("Sample CV text with skills")

    # Clear the override after the test
    app.dependency_overrides.clear()

def test_extract_skills_from_cv_endpoint_invalid_file_type(client: TestClient, mock_current_user: UserDB):
    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.post(
        "/ai_smartjob/extract_skills_from_cv/",
        files={"fichier_cv": ("test.doc", b"some doc content", "application/msword")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Seuls les fichiers PDF sont supportés."

    # # Clear the override after the test
    # app.dependency_overrides.clear()
    # response = client.post(
    #     "/ai_smartjob/extract_skills_from_cv/",
    #     files={"fichier_cv": ("test.doc", b"some doc content", "application/msword")}
    # )
    # assert response.status_code == 400
    # assert response.json()["detail"] == "Seuls les fichiers PDF sont supportés."

def test_extract_skills_from_cv_endpoint_empty_pdf(client: TestClient, mock_current_user: UserDB, mock_pdf_extractor):
    mock_extract_text = mock_pdf_extractor
    mock_extract_text.return_value = "" # Simulate empty text extraction

    dummy_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Parent 2 0 R>>endobj 4 0 obj<</Length 11>>stream\nBT/F1 12 Tf 72 712 Td (Hello) TjET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000110 00000 n\n0000000200 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n221\n%%EOF"

    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.post(
        "/ai_smartjob/extract_skills_from_cv/",
        files={"fichier_cv": ("empty_skills.pdf", dummy_pdf_content, "application/pdf")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Impossible d'extraire le texte du PDF. Le PDF pourrait être vide ou basé sur des images."

    # # Clear the override after the test
    # app.dependency_overrides.clear()
    # mock_extract_text = mock_pdf_extractor
    # mock_extract_text.return_value = "" # Simulate empty text extraction

    # dummy_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Parent 2 0 R>>endobj 4 0 obj<</Length 11>>stream\nBT/F1 12 Tf 72 712 Td (Hello) TjET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000110 00000 n\n0000000200 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n221\n%%EOF"

    # response = client.post(
    #     "/ai_smartjob/extract_skills_from_cv/",
    #     files={"fichier_cv": ("empty_skills.pdf", dummy_pdf_content, "application/pdf")}
    # )
    # assert response.status_code == 400
    # assert response.json()["detail"] == "Impossible d'extraire le texte du PDF. Le PDF pourrait être vide ou basé sur des images."

# def test_read_users_admin_access(client: TestClient, db_session: Session, mock_admin_user: UserDB):
#     # Add some test users
#     db_session.add(UserDB(username="user1", hashed_password=get_password_hash("pass1")))
#     db_session.add(UserDB(username="user2", hashed_password=get_password_hash("pass2")))
#     db_session.commit()

#     # Override get_current_user for this test
#     app.dependency_overrides[get_current_user] = lambda: mock_admin_user

#     response = client.get("/users/")
#     assert response.status_code == 200
#     users = response.json()
#     assert len(users) == 2 # Only user1 and user2, mock_admin_user is not added to db_session here
#     assert any(u["username"] == "user1" for u in users)
#     assert any(u["username"] == "user2" for u in users)

    # # Clear the override after the test
    # app.dependency_overrides.clear()
    # # Add some test users
    # db_session.add(UserDB(username="user1", hashed_password=get_password_hash("pass1")))
    # db_session.add(UserDB(username="user2", hashed_password=get_password_hash("pass2")))
    # db_session.commit()

    # response = client.get("/users/")
    # assert response.status_code == 200
    # users = response.json()
    # assert len(users) == 2 # Only user1 and user2, mock_admin_user is not added to db_session here
    # assert any(u["username"] == "user1" for u in users)
    # assert any(u["username"] == "user2" for u in users)

def test_read_users_non_admin_access(client: TestClient, mock_current_user: UserDB):
    # Override get_current_user for this test
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    response = client.get("/users/")
    assert response.status_code == 403
    assert response.json()["detail"] == "Only admin can view all users"

    # Clear the override after the test
    app.dependency_overrides.clear()

def test_read_users_unauthenticated(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Not authenticated"
