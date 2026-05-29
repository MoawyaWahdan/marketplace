"""

from sqlmodel import create_engine, Session
from app.models.listing import ListingDB, ListingCategory, ListingCondition
import random
import string
from app.models.user import UserDB

LISTINGS_TO_ADD = 4


def generate_random_string(min_length, max_length):

    characters = string.ascii_letters + " "
    length = random.randint(min_length, max_length)
    random_string = "".join(random.choices(characters, k=length))
    return random_string


def generate_listings():
    sqlite_url = "sqlite:///database.db"
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    with Session(engine) as session:
        for i in range(LISTINGS_TO_ADD):
            listing_db = ListingDB(
                title=str(i) + " user 1 " + generate_random_string(5, 100),
                description=generate_random_string(5, 1000),
                seller_id=1,
                price=round(random.uniform(10, 200), 1),
                category=random.choice(list(ListingCategory)),
                condition=random.choice(list(ListingCondition)),
            )

            session.add(listing_db)
        session.commit()


if __name__ == "__main__":
    generate_listings()

"""
