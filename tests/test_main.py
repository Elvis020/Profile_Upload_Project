import os
from http import HTTPStatus
from pathlib import Path

import pytest
import sqlalchemy as sa
from fastapi import File
from requests_toolbelt import MultipartEncoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app import app, get_db
from db import engine, Base
from settings import settings

SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL
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
    base_path = os.path.dirname(__file__)
    image_path = os.path.abspath(os.path.join(base_path, 'tmp/test_image.jpg'))
    _test_upload_file = Path(image_path)
    _files = {'image': _test_upload_file.open('rb')}
    return client.post(
        "/users",
        json={
            "name": "testUser",
            "email": "test@user.com"
        },
        files=_files
    )


class TestAnotherUsers:
    def test_get_all_users(self, client):
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.skip
    def test_create_user_with_no_image(self, create_fake_user, client):
        response = create_fake_user
        print(response.json())

    # @pytest.mark.skip
    def test_create_user(self, client):
        base_path = os.path.dirname(__file__)
        image_path = os.path.abspath(os.path.join(base_path, 'tmp/test_image.jpg'))
        user = {"name": "testUser", "email": "test@user.com"}
        _files = MultipartEncoder(fields={'image': (image_path, open(image_path, 'rb'))})
        headers = {"Content-Type": "multipart/form-data"}
        response = client.post('/users', json=user, data=_files, headers=headers)
        print(response.json())

        # base_path = os.path.dirname(__file__)
        # image_path = os.path.abspath(os.path.join(base_path, 'tmp/test_image.jpg'))
        # with open(image_path, "rb") as f:
        #     response = client.post("/users", json=user, files={"file": ("image", f, "image/jpg")})
        #     print(response.json(), response.status_code)

        # base_path = os.path.dirname(__file__)
        # image_path = os.path.abspath(os.path.join(base_path, 'tmp/test_image.jpg'))
        # _test_upload_file = Path(image_path)
        # _files = {'image': _test_upload_file.open('rb')}
        # response = client.post('/users', json=user, files=_files)

        # print(response.status_code)
        # print(response.json())
        # assert response.status_code == HTTPStatus.CREATED
        # assert response.json() == {
        #     "id": 1,
        #     "name": "Elvis",
        #     "email": "elvis@gmail.com",
        #     "image": None
        # }

    @pytest.mark.skip
    def test_get_specific_user(self, client):
        response = client.get("/users/2", headers={"X-Token": "coneofsilence"})
        assert response.status_code == 200
        print(response.json())
        # assert response.json() == {
        #     "id": 1,
        #     "name": "Elvis",
        #     "email": "elvis@gmail.com",
        #     "profile_image_id": None
        # }

    @pytest.mark.skip
    def test_delete_user(self, client):
        response = client.delete("/users/1", headers={"X-Token": "coneofsilence"})
        assert response.status_code == 204
        assert len(client.get("/users").json()) == 0
