from pydantic import ValidationError
from traffic_contract import TrafficUpdate

# Mock data simulating a messy API response
raw_traffic_data = [
    # Case 1: Perfect data
    {"segment_id": "hwy-01", "current_speed": 85.0, "congestion_level": "LOW"},
    
    # Case 2: Missing congestion level (Needs imputation)
    {"segment_id": "hwy-02", "current_speed": 15.0, "congestion_level": None},
    
    # Case 3: Semantic Error (Urban speeding)
    {"segment_id": "urban-03", "current_speed": 120.0, "congestion_level": "LOW"},
]

def run_pipeline():
    print("--- Starting Traffic Ingestion ---")
    
    for row in raw_traffic_data:
        try:
            # Enforce Contract
            validated_record = TrafficUpdate(**row)
            
            print(f"[OK] Segment: {validated_record.segment_id} | "
                  f"Speed: {validated_record.current_speed} | "
                  f"Congestion: {validated_record.congestion_level} (Final)")
                  
        except ValidationError as e:
            # In a real system -> Send to DLQ
            reason = e.errors()[0]['msg']
            print(f"[REJECTED] Segment: {row.get('segment_id')} | Reason: {reason}")

if __name__ == "__main__":
    run_pipeline()
