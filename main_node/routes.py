from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from models import Node, NodeCreate, ModelInfo
from utils import get_db
from sqlalchemy.exc import SQLAlchemyError
import requests

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
            existing_node.models += node.models
            existing_node.ip = node.ip
            message = "Node updated successfully"
        else:
            new_node = Node(
                node_id=node.node_id,
                status=node.status,
                resources=node.resources,
                models=node.models,
                ip=node.ip
            )
            db.add(new_node)
            message = "Node registered successfully"

        db.commit()
        return {"message": message}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nodes")
async def list_nodes(db: Session = Depends(get_db)):
    nodes = db.query(Node).all()
    return nodes

@router.post("/register-models")
async def register_model(model: ModelInfo, db: Session = Depends(get_db)):
    # Обработка данных о модели
    print(f"Registered models: {model.models}")
    return {"status": "success"}

@router.api_route("/proxy/{node_id}/{endpoint:path}", methods=["GET", "POST"])
async def proxy_request(
    node_id: str,
    endpoint: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Проксирование запросов между нодами через Main Node.
    """
    # Поиск целевой ноды (например, child_node_b)
    try:
        node = db.query(Node).filter(Node.node_id == node_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")

    if not node:
        raise HTTPException(status_code=404, detail="Узел не найден")

    # Формируем URL целевого узла
    # target_url = f"{node.url}/{endpoint}" # на самом деле тут не node.url а node_id


    # target_url = f"{node_id}/{endpoint}"
    # target_url = f'http://{node.ip}/api'
    # target_url = f'http://{node.ip}/{endpoint}'
    target_url = f'http://{node.ip}/{endpoint}' if endpoint else f'http://{node.ip}/api'
    print(f"Target URL: {target_url}")



    try:
        # Проксирование GET или POST запроса
        
        if request.method == "POST":
            try:
                body = await request.json()  # Получаем тело запроса
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Некорректный JSON в запросе: {e}")
            response = requests.post(target_url, json=body)
        else:
            query_params = dict(request.query_params)  # Параметры GET
            response = requests.get(target_url, params=query_params)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ошибка при обращении к ноде: {response.text}"
    )


        # Возвращаем ответ
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при проксировании: {str(e)}")