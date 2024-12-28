from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from pydantic import BaseModel
from typing import List, Dict

Base = declarative_base()

class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False, default="unknown")
    resources = Column(JSON, nullable=True, default={})
    models = Column(ARRAY(String), nullable=True, default=[])
    ip = Column(String, unique=True, nullable=False, default="127.0.0.1")

class NodeCreate(BaseModel):
    node_id: str
    status: str = "unknown"
    resources: Dict = {}
    models: List[str] = []
    ip: str = "127.0.0.1"

class ModelInfo(BaseModel):
    models: List[str]
