from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
import os
from jinja2 import Template

# Конфигурация приложения и базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/main_db")

# Инициализация базы данных
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Определение модели базы данных
class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    resources = Column(JSON, nullable=True)

# Создание таблиц
Base.metadata.create_all(engine)

# Модели запросов и ответов
class NodeCreate(BaseModel):
    node_id: str
    status: str = "unknown"
    resources: dict = {}

# FastAPI приложение
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
async def register_node(node: NodeCreate, db: Session = Depends(get_db)):
    """
    Регистрация или обновление информации о ноде.
    """
    try:
        # Проверка на существующий нод
        existing_node = db.query(Node).filter_by(node_id=node.node_id).first()
        if existing_node:
            existing_node.status = node.status
            existing_node.resources = node.resources
            message = "Node updated successfully"
        else:
            # Создание нового нода
            new_node = Node(
                node_id=node.node_id,
                status=node.status,
                resources=node.resources
            )
            db.add(new_node)
            message = "Node registered successfully"

        db.commit()
        return {"message": message}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nodes", response_model=List[NodeCreate])
async def list_nodes(db: Session = Depends(get_db)):
    """
    Получение списка всех зарегистрированных узлов.
    """
    nodes = db.query(Node).all()
    return nodes
# Главная точка входа
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
