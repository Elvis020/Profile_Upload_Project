import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app, get_db
from db import Base

#  TODO: Use dotenv for these urls
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost/test-fastapi-test"

test_engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    # Dependency override
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def create_fake_user(client):
    return client.post(
        "/users",
        headers={"X-Token": "coneofsilence"},
        json={"name": "Elvis", "email": "elvis@gmail.com"},
    )

def test_get_all_users(client):
    response = client.get("/users", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 200
    assert response.json() == []


def test_create_user(client, create_fake_user):
    assert create_fake_user.status_code == 201
    assert create_fake_user.json() == {
        "id": 1,
        "name": "Elvis",
        "email": "elvis@gmail.com",
    }


def test_get_specific_user(client, create_fake_user):
    response = client.get("/user/1", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Elvis",
        "email": "elvis@gmail.com",
    }


def test_delete_user(client, create_fake_user):
    response = client.delete("/users/1", headers={"X-Token": "coneofsilence"})
    check_for_all_users = client.get("/users", headers={"X-Token": "coneofsilence"})
    assert response.status_code == 204
    assert len(check_for_all_users.json()) == 0
