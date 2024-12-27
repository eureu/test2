from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# Конфигурация приложения и базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/main_db")

# Инициализация базы данных
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()