from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from db.models import Base, User
from db.seed_data import seed_database

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created")

    # Check if demo user exists
    session = SessionLocal()
    try:
        demo_user = (
            session.query(User).filter(User.email == "demo@motomatch.local").first()
        )
    finally:
        session.close()

    if not demo_user:
        print("[..] Seeding database...")
        seed_database(engine, SessionLocal)
        print("[OK] Database seeded with sample data")
    else:
        print("[--] Database already seeded, skipping...")
