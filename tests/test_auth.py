from fastapi import status


def test_login(client, user):

    # Login
    response = client.post(
        "/token", data={"username": user["username"], "password": user["password"]}
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"].lower() == "bearer"


def test_login_wrong_password(client, user):

    # Login
    response = client.post(
        "/token", data={"username": user["username"], "password": "123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_unknown_username(client, user):

    # Login
    response = client.post(
        "/token", data={"username": "sanjose", "password": user["password"]}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_non_exist_user(client):

    response = client.post("/token", data={"username": "sanjose", "password": "123"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_missing_fields(client):
    response = client.post("/token", data={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
