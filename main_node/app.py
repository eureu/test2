from fastapi import FastAPI
from routes import router
from models import Base
from utils import engine

# Создание таблиц
Base.metadata.create_all(engine)

# FastAPI приложение
app = FastAPI()

# Регистрация маршрутов
app.include_router(router)

# Главная точка входа
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)