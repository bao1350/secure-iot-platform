from pydantic import BaseModel


class MeasureCreate(BaseModel):
    sensor_id: int
    temperature: float
    humidity: float
    battery: float


class UserCreate(BaseModel):
    email: str
    hashed_password: str