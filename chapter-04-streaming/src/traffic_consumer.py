import json
from kafka import KafkaConsumer
from pydantic import ValidationError

# Import the contract from Chapter 3 (make sure path allows this import)
# For simplicity in this lab, we redefine the minimal model here or assume it's available
from pydantic import BaseModel, Field

class TrafficUpdate(BaseModel):
    segment_id: str
    current_speed: float = Field(ge=0, le=200)

def start_consumer():
    print("--- Starting Traffic Consumer (Waiting for data...) ---")
    consumer = KafkaConsumer(
        'traffic_updates',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    for message in consumer:
        try:
            # 1. Validation in Motion
            data = TrafficUpdate(**message.value)
            
            # 2. Business Logic (e.g., detect congestion)
            status = "CONGESTED" if data.current_speed < 20 else "FREE"
            
            print(f"[STREAM] Processing: {data.segment_id} | Speed: {data.current_speed} -> Status: {status}")

        except ValidationError as e:
            # 3. Error Handling (Log & Skip)
            print(f"[ERROR] Malformed data skipped: {message.value} | Reason: {e}")
        except Exception as e:
            print(f"[SYSTEM ERROR] {e}")

if __name__ == "__main__":
    start_consumer()
