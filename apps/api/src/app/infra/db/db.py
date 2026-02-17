import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não definida!")

MAX_RETRIES = 10
RETRY_DELAY = 3

engine = None
for attempt in range(MAX_RETRIES):
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Conexão com banco OK!")
        break
    except OperationalError as e:
        print(f"Tentativa {attempt+1}/{MAX_RETRIES} falhou: {e}")
        if attempt == MAX_RETRIES - 1:
            raise
        time.sleep(RETRY_DELAY)

if engine is None:
    raise RuntimeError("Não foi possível conectar ao banco após retries")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
