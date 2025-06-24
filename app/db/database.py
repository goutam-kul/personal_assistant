from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DB_URL = os.getenv("DATABASE_URL")
if DB_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        