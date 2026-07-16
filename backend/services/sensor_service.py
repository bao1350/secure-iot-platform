from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from backend.models import Measure, Sensor, User


def get_user_sensor(sensor_id: int, user: User, db: Session) -> Sensor:
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Capteur non trouvé")

    if sensor.user_id != user.id:
        raise HTTPException(status_code=403, detail="Ce capteur ne vous appartient pas")

    return sensor


def get_latest_measure(sensor_id: int, db: Session) -> Optional[Measure]:
    return (
        db.query(Measure)
        .filter(Measure.sensor_id == sensor_id)
        .order_by(Measure.timestamp.desc())
        .first()
    )


def get_sensor_history(sensor: Sensor, period: str, db: Session) -> List[dict]:
    now = datetime.utcnow()

    if period == "today":
        start = datetime(year=now.year, month=now.month, day=now.day)
        bucket_seconds = 10 * 60
    elif period == "week":
        start = now - timedelta(days=7)
        bucket_seconds = 60 * 60
    elif period == "month":
        start = now - timedelta(days=30)
        bucket_seconds = 6 * 60 * 60
    else:
        raise HTTPException(
            status_code=400,
            detail="Paramètre 'period' invalide. Utiliser 'today', 'week' ou 'month'"
        )

    bucket = func.to_timestamp(
        func.floor(func.extract("epoch", Measure.timestamp) / bucket_seconds) * bucket_seconds
    ).label("bucket")

    results = (
        db.query(
            bucket,
            func.avg(Measure.temperature).label("temperature"),
            func.avg(Measure.humidity).label("humidity"),
            func.avg(Measure.battery).label("battery"),
        )
        .filter(
            Measure.sensor_id == sensor.id,
            Measure.timestamp >= start,
        )
        .group_by(bucket)
        .order_by(bucket.asc())
        .all()
    )

    history = []
    for row in results:
        timestamp = row.bucket
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        history.append({
            "timestamp": timestamp,
            "temperature": round(row.temperature, 2),
            "humidity": round(row.humidity, 2),
            "battery": round(row.battery, 2),
        })

    return history


def list_dashboard_sensors(user: User, db: Session) -> List[dict]:
    sensors = db.query(Sensor).filter(Sensor.user_id == user.id).all()
    dashboard = []

    for sensor in sensors:
        dashboard.append({
            "id": sensor.id,
            "name": sensor.name,
            "room": sensor.room,
            "sensor_type": sensor.sensor_type,
            "measure": get_latest_measure(sensor.id, db)
        })

    return dashboard


def delete_sensor(sensor: Sensor, db: Session) -> None:
    db.delete(sensor)
    db.commit()

    if db.query(Sensor).count() == 0:
        db.execute(text("ALTER SEQUENCE sensors_id_seq RESTART WITH 1"))
        db.commit()
