from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

from database import Base


class Measure(Base):
    __tablename__ = "measures"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer)
    temperature = Column(Float)
    humidity = Column(Float)
    battery = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)