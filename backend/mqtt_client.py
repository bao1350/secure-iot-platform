import json
import paho.mqtt.client as mqtt

from backend.database import SessionLocal
from backend.config import MQTT_HOST, MQTT_PORT
from backend.models import Measure
from backend.ws_manager import manager

MQTT_MEASURES_TOPIC_FILTER = "iot/sensors/+/measures"


def sensor_id_from_topic(topic: str) -> int:
    """Return the sensor identifier from iot/sensors/{id}/measures."""
    parts = topic.split("/")
    if len(parts) != 4 or parts[0] != "iot" or parts[1] != "sensors" or parts[3] != "measures":
        raise ValueError(f"Topic MQTT invalide : {topic}")

    return int(parts[2])


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("✅ Connecté au broker MQTT")
        client.subscribe(MQTT_MEASURES_TOPIC_FILTER)
    else:
        print(f"❌ Erreur de connexion MQTT : {reason_code}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        sensor_id = sensor_id_from_topic(msg.topic)

        # Le topic est la source d'autorité : le payload ne doit pas désigner
        # un autre capteur.
        if data.get("sensor_id") != sensor_id:
            raise ValueError("sensor_id du payload différent de celui du topic")
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        print(f"❌ Message MQTT ignoré ({msg.topic}) : {error}")
        return

    print(f"📩 Message reçu : {data}")

    db = SessionLocal()

    try:
        measure = Measure(
            sensor_id=sensor_id,
            temperature=data["temperature"],
            humidity=data["humidity"],
            battery=data["battery"]
        )

        db.add(measure)
        db.commit()

        print("✅ Mesure enregistrée dans PostgreSQL")
        manager.broadcast_from_thread(json.dumps({
            "sensor_id": sensor_id,
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "battery": data["battery"],
            "timestamp": data.get("timestamp")
        }))

    except Exception as e:
        db.rollback()
        print("❌ Erreur :", e)

    finally:
        db.close()


def start_mqtt():
    print(">>> start_mqtt appelé")

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        client.on_connect = on_connect
        client.on_message = on_message

        print(">>> Connexion à Mosquitto...")

        client.connect(MQTT_HOST, MQTT_PORT, 60)

        print(">>> Connecté, attente des messages...")

        client.loop_forever()

    except Exception as e:
        print("ERREUR MQTT :", e)
