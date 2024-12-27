from sqlalchemy import Column, Integer, String, JSON, List
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

# Инициализация базы данных
Base = declarative_base()

# Определение модели базы данных
class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    resources = Column(JSON, nullable=True)
    models = Column(List, nullable=True)

# Модели запросов и ответов
class NodeCreate(BaseModel):
    node_id: str
    status: str = "unknown"
    resources: dict = {}
    models: list = []


class ModelInfo(BaseModel):
    models: List[str]  # Список моделей
