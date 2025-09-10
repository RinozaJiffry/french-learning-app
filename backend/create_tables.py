# create_tables.py
# Run this script to create all tables defined in app/models.py in the target DATABASE_URL

from app.database import engine, Base  # uses DATABASE_URL from .env or default
from app import models  # noqa: F401 ensure models are imported so metadata is populated


def main():
    print("Creating tables using SQLAlchemy metadata...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created (if they did not already exist).")


if __name__ == "__main__":
    main()
