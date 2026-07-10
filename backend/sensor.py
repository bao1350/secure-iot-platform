import paho.mqtt.client as mqtt
import json
import time
import random


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)


client.connect(
    "localhost",
    1883,
    60
)

client.loop_start()


while True:

    data = {
        "sensor_id": 1,
        "temperature": round(random.uniform(20, 25), 2),
        "humidity": random.randint(40, 60),
        "battery": 90
    }

    client.publish(
        "iot/sensor/1",
        json.dumps(data)
    )

    print("📡 Envoi :", data)

    time.sleep(5)