from fastapi import FastAPI
from routes import router
from models import Base
from utils import engine
from db_monitor import monitor_database

Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
    monitor_database()