from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas import MeasureCreate
from backend.deps import get_db
from backend.auth import get_current_user, validate_csrf
from backend.models import Measure, Sensor
from backend.services.sensor_service import get_user_sensor

router = APIRouter(prefix="/measures", tags=["Measures"])


@router.post("/")
def create_measure(
    measure: MeasureCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _: None = Depends(validate_csrf),
):
    sensor = get_user_sensor(measure.sensor_id, user, db)

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


@router.get("/latest")
def get_latest_measure(db: Session = Depends(get_db), user=Depends(get_current_user)):
    measure = (
        db.query(Measure)
        .join(Sensor)
        .filter(Sensor.user_id == user.id)
        .order_by(Measure.timestamp.desc())
        .first()
    )

    return measure


@router.get("/history")
def get_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    measures = (
        db.query(Measure)
        .join(Sensor)
        .filter(Sensor.user_id == user.id)
        .order_by(Measure.timestamp.desc())
        .all()
    )

    return measures
