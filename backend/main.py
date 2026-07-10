from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Measure, User
from schemas import MeasureCreate, UserCreate
from mqtt_client import start_mqtt

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):

    mqtt_thread = threading.Thread(
        target=start_mqtt,
        daemon=True
    )

    mqtt_thread.start()

    print("🚀 Client MQTT démarré")

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Secure IoT Platform"}


@app.get("/status")
def get_status():
    return {"status": "ok"}


@app.post("/measure")
def create_measure(
    measure: MeasureCreate,
    db: Session = Depends(get_db)
):
    new_measure = Measure(
        sensor_id=measure.sensor_id,
        temperature=measure.temperature,
        humidity=measure.humidity,
        battery=measure.battery
    )

    db.add(new_measure)
    db.commit()
    db.refresh(new_measure)

    return new_measure


@app.post("/user")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    new_user = User(
        email=user.email,
        hashed_password=user.hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user