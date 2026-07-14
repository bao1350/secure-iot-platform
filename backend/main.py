from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Measure, Sensor, User
from schemas import MeasureCreate, SensorCreate, UserCreate
from mqtt_client import start_mqtt
from security import hash_password, verify_password
from auth import create_access_token, get_current_user


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Secure IoT Platform"}


@app.get("/status")
def get_status():
    return {"status": "ok"}



# ======================
# MESURES
# ======================

@app.post("/measure")
def create_measure(
    measure: MeasureCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    sensor = (
        db.query(Sensor)
        .filter(
            Sensor.id == measure.sensor_id,
            Sensor.user_id == user.id
        )
        .first()
    )

    if sensor is None:
        raise HTTPException(
            status_code=403,
            detail="Ce capteur ne vous appartient pas"
        )


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



@app.get("/measures/latest")
def get_latest_measure(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    measure = (
        db.query(Measure)
        .join(Sensor)
        .filter(
            Sensor.user_id == user.id
        )
        .order_by(
            Measure.timestamp.desc()
        )
        .first()
    )

    return measure



# ======================
# CAPTEURS
# ======================

@app.post("/sensor")
def create_sensor(
    sensor: SensorCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    new_sensor = Sensor(
        name=sensor.name,
        room=sensor.room,
        sensor_type=sensor.sensor_type,
        user_id=user.id
    )

    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)

    return new_sensor

@app.delete("/sensor/{sensor_id}")
def delete_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    sensor = (
        db.query(Sensor)
        .filter(
            Sensor.id == sensor_id,
            Sensor.user_id == user.id
        )
        .first()
    )

    if sensor is None:
        raise HTTPException(
            status_code=404,
            detail="Capteur non trouvé"
        )


    db.delete(sensor)
    db.commit()
    
    if db.query(Sensor).count() == 0:
        db.execute(text("ALTER SEQUENCE sensors_id_seq RESTART WITH 1"))
        db.commit()

    return {
        "message": "Capteur supprimé avec succès"
    }

@app.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    sensors = (
        db.query(Sensor)
        .filter(
            Sensor.user_id == user.id
        )
        .all()
    )

    dashboard = []

    for sensor in sensors:

        latest_measure = (
            db.query(Measure)
            .filter(
                Measure.sensor_id == sensor.id
            )
            .order_by(
                Measure.timestamp.desc()
            )
            .first()
        )

        dashboard.append({
            "id": sensor.id,
            "name": sensor.name,
            "room": sensor.room,
            "sensor_type": sensor.sensor_type,
            "measure": latest_measure
        })

    return dashboard



# ======================
# AUTH
# ======================

@app.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(
            User.email == user.email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Cet email est déjà utilisé"
        )


    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Utilisateur créé avec succès"
    }



@app.post("/login")
def login(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(
            User.email == user.email
        )
        .first()
    )


    if db_user is None:
        raise HTTPException(
            status_code=400,
            detail="Utilisateur inconnu"
        )


    if not verify_password(
        user.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Mot de passe incorrect"
        )


    token = create_access_token(
        {
            "sub": db_user.email
        }
    )


    return {
        "access_token": token,
        "token_type": "bearer"
    }