from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from models import Node, NodeCreate, ModelInfo
from utils import get_db
from sqlalchemy.exc import SQLAlchemyError
import requests
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/register")
async def register_node(node: NodeCreate, request: Request, db: Session = Depends(get_db)):
    client_host = request.client.host
    forwarded_for = request.headers.get("X-Forwarded-For")
    real_ip = request.headers.get("X-Real-IP")
    client_ip = forwarded_for.split(",")[0] if forwarded_for else (real_ip or client_host)

    try:
        existing_node = db.query(Node).filter_by(node_id=node.node_id).first()
        if existing_node:
            existing_node.status = node.status
            existing_node.resources = node.resources
            existing_node.models += node.models
            existing_node.ip = client_ip
            message = "Node updated successfully"
        else:
            new_node = Node(
                node_id=node.node_id,
                status=node.status,
                resources=node.resources,
                models=node.models,
                ip=client_ip
            )
            db.add(new_node)
            message = "Node registered successfully"

        db.commit()
        return {"message": message, "client_ip": client_ip}
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
    try:
        node = db.query(Node).filter(Node.node_id == node_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")

    if not node:
        raise HTTPException(status_code=404, detail="Узел не найден")

    target_url = f'http://{node.ip}:80/{endpoint}' if endpoint else f'http://{node.ip}:80/api'
    print(f"Target URL: {target_url}")



    try:
        if request.method == "POST":
            try:
                body = await request.json()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Некорректный JSON в запросе: {e}")
            response = requests.post(target_url, json=body)
        else:
            query_params = dict(request.query_params)
            response = requests.get(target_url, params=query_params)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ошибка при обращении к ноде: {response.text}"
    )


        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при проксировании: {str(e)}")