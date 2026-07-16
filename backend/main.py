from contextlib import asynccontextmanager
import asyncio
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.mqtt_client import start_mqtt
from backend.routers import auth_router, measures_router, sensors_router, ws_router
from backend.ws_manager import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    manager.set_loop(loop)
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()
    print("🚀 Client MQTT démarré")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(measures_router)
app.include_router(sensors_router)
app.include_router(ws_router)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Secure IoT Platform"}


@app.get("/status")
def get_status():
    return {"status": "ok"}
