from app.models.user import UserDB
from sqlalchemy import select


def test_create_user(client, session):
    response = client.post(
        "/users/",
        json={
            "username": "tempe",
            "password": "abc",
            "email": "tempe@gmail.com",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "tempe"
    assert data["email"] == "tempe@gmail.com"

    db_user = session.scalars(select(UserDB).where(UserDB.username == "tempe")).first()

    assert db_user is not None


def test_duplicate_username(client, session, user):
    response = client.post(
        "/users/",
        json={
            "username": user["username"],
            "password": "newpass",
            "email": "new_email@gmail.com",
        },
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

    db_user = session.scalars(
        select(UserDB).where(UserDB.email == "new_email@gmail.com")
    ).first()

    assert db_user is None


def test_duplicate_email(client, session, user):
    response = client.post(
        "/users/",
        json={
            "username": "new_username",
            "password": "abc",
            "email": user["email"],
        },
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

    # original user still exists
    original_user = session.scalars(
        select(UserDB).where(UserDB.username == user["username"])
    ).first()
    assert original_user is not None

    new_user = session.scalars(
        select(UserDB).where(UserDB.username == "new_username")
    ).first()
    assert new_user is None
