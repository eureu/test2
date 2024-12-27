from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Node, NodeCreate
from utils import get_db
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

@router.post("/register")
async def register_node(node: NodeCreate, db: Session = Depends(get_db)):
    """
    Регистрация или обновление информации о ноде.
    """
    try:
        existing_node = db.query(Node).filter_by(node_id=node.node_id).first()
        if existing_node:
            existing_node.status = node.status
            existing_node.resources = node.resources
            message = "Node updated successfully"
        else:
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

# @router.get("/nodes", response_model=List[NodeCreate])
@router.get("/nodes")
async def list_nodes(db: Session = Depends(get_db)):
    """
    Получение списка всех зарегистрированных узлов.
    """
    nodes = db.query(Node).all()
    return nodes

@router.post("/register_model")
async def register_model(model: ModelInfo):
    # Обработка данных о модели
    print(f"Registered model: {model.model_name}")
    return {"status": "success"}