import os

from dotenv import load_dotenv


load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"La variable d'environnement {name} est obligatoire.")
    return value


def required_int_env(name: str) -> int:
    value = required_env(name)
    try:
        return int(value)
    except ValueError as error:
        raise RuntimeError(f"La variable d'environnement {name} doit être un entier.") from error


DATABASE_URL = required_env("DATABASE_URL")
MQTT_HOST = required_env("MQTT_HOST")
MQTT_PORT = required_int_env("MQTT_PORT")
SECRET_KEY = required_env("SECRET_KEY")
ALGORITHM = required_env("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = required_int_env("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = required_int_env("REFRESH_TOKEN_EXPIRE_DAYS")
COOKIE_SECURE = required_env("COOKIE_SECURE").lower() == "true"
