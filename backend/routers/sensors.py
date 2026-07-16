from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas import SensorCreate
from backend.deps import get_db
from backend.auth import get_current_user, validate_csrf
from backend.models import Sensor
from backend.services.sensor_service import (
    delete_sensor,
    get_user_sensor,
    get_latest_measure,
    get_sensor_history,
    list_dashboard_sensors,
)

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.post("/")
def create_sensor(
    sensor: SensorCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _: None = Depends(validate_csrf),
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


@router.delete("/{sensor_id}")
def delete_sensor_route(
    sensor_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _: None = Depends(validate_csrf),
):
    sensor = get_user_sensor(sensor_id, user, db)
    delete_sensor(sensor, db)

    return {"message": "Capteur supprimé avec succès"}


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return list_dashboard_sensors(user, db)


@router.get("/{sensor_id}")
def get_sensor(sensor_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sensor = get_user_sensor(sensor_id, user, db)
    latest_measure = get_latest_measure(sensor.id, db)

    return {"sensor": sensor, "latest_measure": latest_measure}


@router.get("/{sensor_id}/history")
def get_sensor_history_route(
    sensor_id: int,
    period: str = "today",
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    sensor = get_user_sensor(sensor_id, user, db)
    return get_sensor_history(sensor, period, db)
