import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

segments = ["hwy-01", "hwy-02", "urban-05", "urban-09"]

print("--- Sending Traffic Events ---")
try:
    while True:
        data = {
            "segment_id": random.choice(segments),
            "current_speed": round(random.uniform(-10, 120), 1) # Note: -10 is invalid!
        }
        producer.send('traffic_updates', value=data)
        print(f"Sent: {data}")
        time.sleep(1) # Simulate real-time stream
except KeyboardInterrupt:
    print("Stopped.")
