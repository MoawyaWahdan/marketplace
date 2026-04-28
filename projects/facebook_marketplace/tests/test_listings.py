from app.models.user import UserDB
from app.models.listing import ListingDB, ListingCondition, ListingCategory
from sqlmodel import select
from fastapi import status


def test_create_listing(client, session):
    # Create user
    response = client.post(
        "/users/",
        json={"username": "tempe", "password": "abc", "email": "tempe@gmail.com"},
    )
    assert response.status_code == 200

    user = session.exec(select(UserDB).where(UserDB.username == "tempe")).first()

    # Login
    response = client.post("/token", data={"username": "tempe", "password": "abc"})
    assert response.status_code == 200

    login_data = response.json()
    token = login_data["access_token"]

    # Create listing
    response = client.post(
        "/listings/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "6x9 rug",
            "price": 99,
            "description": "Beautiful 6x9 rug",
            "condition": ListingCondition.NEW,
            "category": ListingCategory.HOME_ESSENTIALS,
        },
    )

    assert response.status_code == 200

    listing_data = response.json()
    assert "id" in listing_data
    assert listing_data["title"] == "6x9 rug"
    assert listing_data["price"] == 99
    assert listing_data["description"] == "Beautiful 6x9 rug"
    assert listing_data["condition"] == ListingCondition.NEW.value
    assert listing_data["category"] == ListingCategory.HOME_ESSENTIALS.value
    assert listing_data["seller_id"] == user.id

    # DB verification
    listing = session.exec(
        select(ListingDB).where(ListingDB.id == listing_data["id"])
    ).first()

    assert listing is not None
    assert listing.title == "6x9 rug"
    assert listing.price == 99
    assert listing.condition == ListingCondition.NEW
    assert listing.category == ListingCategory.HOME_ESSENTIALS
    assert listing.seller_id == user.id


def test_create_with_invalid_token(client, session):

    # Create listing
    response = client.post(
        "/listings/",
        headers={"Authorization": "Bearer invalid_token"},
        json={
            "title": "6x9 rug",
            "price": 99,
            "description": "Beautiful 6x9 rug",
            "condition": 1,
            "category": 1,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    listing = session.exec(
        select(ListingDB).where(ListingDB.title == "6x9 rug")
    ).first()

    assert listing is None


def test_create_without_token(client, session):
    response = client.post(
        "/listings/",
        json={
            "title": "6x9 rug",
            "price": 99,
            "description": "Beautiful 6x9 rug",
            "condition": 1,
            "category": 1,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    listing = session.exec(
        select(ListingDB).where(ListingDB.title == "6x9 rug")
    ).first()

    assert listing is None
