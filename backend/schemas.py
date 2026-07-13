from pydantic import BaseModel


class MeasureCreate(BaseModel):
    sensor_id: int
    temperature: float
    humidity: float
    battery: float


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class SensorCreate(BaseModel):
    name: str
    room: str
    sensor_type: str