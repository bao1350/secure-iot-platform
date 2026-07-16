from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    # Un utilisateur possède plusieurs capteurs
    sensors = relationship(
        "Sensor",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )



class Sensor(Base):

    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    room = Column(String, nullable=False)

    sensor_type = Column(String, nullable=False)


    # Le capteur appartient à un utilisateur
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )


    user = relationship(
        "User",
        back_populates="sensors"
    )


    # Un capteur possède plusieurs mesures
    measures = relationship(
        "Measure",
        back_populates="sensor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )



class Measure(Base):

    __tablename__ = "measures"
    __table_args__ = (
        CheckConstraint("humidity >= 0 AND humidity <= 100", name="ck_measures_humidity_range"),
        CheckConstraint("battery >= 0 AND battery <= 100", name="ck_measures_battery_range"),
        CheckConstraint("temperature >= -80 AND temperature <= 100", name="ck_measures_temperature_range"),
        Index("ix_measures_sensor_timestamp", "sensor_id", "timestamp"),
    )

    id = Column(Integer, primary_key=True)


    # La mesure appartient à un capteur
    sensor_id = Column(
        Integer,
        ForeignKey("sensors.id", ondelete="CASCADE"),
        nullable=False,
    )


    temperature = Column(Float, nullable=False)

    humidity = Column(Float, nullable=False)

    battery = Column(Float, nullable=False)

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )


    sensor = relationship(
        "Sensor",
        back_populates="measures"
    )
