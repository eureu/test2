from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from pydantic import BaseModel
from typing import List, Dict

# Инициализация базы данных
Base = declarative_base()

# Определение модели базы данных
class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False, default="unknown")
    resources = Column(JSON, nullable=True, default={})
    models = Column(ARRAY(String), nullable=True, default=[])

# Модели запросов и ответов
class NodeCreate(BaseModel):
    node_id: str
    status: str = "unknown"
    resources: Dict = {}
    models: List[str] = []

class ModelInfo(BaseModel):
    models: List[str]  # Список моделей
