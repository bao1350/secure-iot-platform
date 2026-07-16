import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class MeasureCreate(BaseModel):
    sensor_id: int
    temperature: float
    humidity: float
    battery: float


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        requirements = (r"[a-z]", r"[A-Z]", r"\d", r"[^\w\s]")
        if not all(re.search(pattern, password) for pattern in requirements):
            raise ValueError("Le mot de passe doit contenir majuscule, minuscule, chiffre et caractère spécial.")
        return password


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class SensorCreate(BaseModel):
    name: str
    room: str
    sensor_type: str
