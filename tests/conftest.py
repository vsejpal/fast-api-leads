import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from typing import Generator, Dict

from app.main import app
from app.db.session import get_db
from app.db.models import Base
from app.crud import users as users_crud

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test upload directory
TEST_UPLOAD_DIR = "test_uploads"
if not os.path.exists(TEST_UPLOAD_DIR):
    os.makedirs(TEST_UPLOAD_DIR)

@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)
    
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db: TestingSessionLocal) -> Generator:
    """
    Create a new FastAPI TestClient that uses the `db` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    def _get_test_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db: TestingSessionLocal) -> Dict[str, str]:
    """
    Create a test user and return their credentials.
    """
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    users_crud.create_user(db, user_data["email"], user_data["password"])
    return user_data

@pytest.fixture(scope="function")
def test_user_token(client: TestClient, test_user: Dict[str, str]) -> str:
    """
    Create a test user and return a valid token for them.
    """
    response = client.post(
        "/api/auth/token",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def authorized_client(client: TestClient, test_user_token: str) -> TestClient:
    """
    Return a client with valid authorization headers.
    """
    client.headers["Authorization"] = f"Bearer {test_user_token}"
    return client

@pytest.fixture(autouse=True)
def cleanup_test_uploads():
    """
    Clean up test upload directory after each test.
    """
    yield
    for file in os.listdir(TEST_UPLOAD_DIR):
        os.remove(os.path.join(TEST_UPLOAD_DIR, file)) 