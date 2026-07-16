import paho.mqtt.client as mqtt
import json
import time
import random

client = mqtt.Client()

client.connect("localhost", 1883)

while True:

    for sensor_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:

        data = {
            "sensor_id": sensor_id,
            "temperature": round(random.uniform(20, 25), 2),
            "humidity": random.randint(40, 60),
            "battery": random.randint(80, 100)
        }

        client.publish(
            f"iot/sensors/{sensor_id}/measures",
            json.dumps(data)
        )

        print(data)

    time.sleep(5)
