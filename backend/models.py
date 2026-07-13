from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    room = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False)

    measures = relationship("Measure", back_populates="sensor")


class Measure(Base):
    __tablename__ = "measures"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))

    temperature = Column(Float)
    humidity = Column(Float)
    battery = Column(Float)

    timestamp = Column(DateTime, default=datetime.utcnow)

    sensor = relationship("Sensor", back_populates="measures")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)