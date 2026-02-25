import os
import time
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

# Ensure apps/api/.env is loaded even when running commands from repo root.
ENV_PATH = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(f"DATABASE_URL not set. Check: {ENV_PATH}")

MAX_RETRIES = 10
RETRY_DELAY = 3

engine = None
for attempt in range(MAX_RETRIES):
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection OK")
        break
    except OperationalError as e:
        print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
        if attempt == MAX_RETRIES - 1:
            raise
        time.sleep(RETRY_DELAY)

if engine is None:
    raise RuntimeError("Could not connect to database after retries")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
