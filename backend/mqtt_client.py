import json
import paho.mqtt.client as mqtt

from backend.database import SessionLocal
from backend.models import Measure


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("✅ Connecté au broker MQTT")
        client.subscribe("iot/sensor/+")
    else:
        print(f"❌ Erreur de connexion MQTT : {reason_code}")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    print(f"📩 Message reçu : {data}")

    db = SessionLocal()

    try:
        measure = Measure(
            sensor_id=data["sensor_id"],
            temperature=data["temperature"],
            humidity=data["humidity"],
            battery=data["battery"]
        )

        db.add(measure)
        db.commit()

        print("✅ Mesure enregistrée dans PostgreSQL")

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

        client.connect("mosquitto", 1883, 60)

        print(">>> Connecté, attente des messages...")

        client.loop_forever()

    except Exception as e:
        print("ERREUR MQTT :", e)