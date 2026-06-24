from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "invoice_dashboard.db"

DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

print("USING DATABASE:", DB_PATH)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()