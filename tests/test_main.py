import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.config import Config
import sqlalchemy as sa
from starlette.testclient import TestClient

from app import app, get_db
from db import engine, Base

config = Config('../.env')
USER = config('DB_USER')
PASSWORD = config('DB_PASSWORD')
DB_TABLE = config('TEST_DB_NAME')

SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@localhost/{DB_TABLE}"

test_engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture()
def create_fake_user(client):
    return client.post(
        "/users",
        headers={"X-Token": "coneofsilence"},
        json={"name": "Elvis", "email": "elvis@gmail.com"},
    )


class TestAnotherUsers:
    def test_get_all_users(self, client):
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_user(self, create_fake_user, client):
        response = create_fake_user
        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "name": "Elvis",
            "email": "elvis@gmail.com",
        }

    def test_get_specific_user(self, client):
        response = client.get("/users/1", headers={"X-Token": "coneofsilence"})
        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "Elvis",
            "email": "elvis@gmail.com",
        }

    def test_delete_user(self, client):
        response = client.delete("/users/1", headers={"X-Token": "coneofsilence"})
        assert response.status_code == 204
        assert len(client.get("/users").json())== 0