from src.infrastructure.chroma_store import ChromaVectorStore
from src.services.text_ingestion import TextIngestionService

def run_production_ingestion():
    # 1. Initialize Infrastructure (The 'Database')
    vector_db = ChromaVectorStore(collection_name="logismart_policies")
    
    # Reset DB to avoid duplicates in lab
    vector_db.reset() 

    # 2. Initialize Service (The 'Logic')
    ingestion_service = TextIngestionService(vector_store=vector_db)
    
    # 3. Execute Business Logic
    sample_policy = """
    LogiSmart Driver Policy 2026 - Official Handbook

    1. Speed Limits and Traffic Compliance
    All LogiSmart drivers must strictly adhere to local speed limits at all times. In urban areas, the maximum speed limit is 30 km/h, regardless of signage indicating higher limits, to ensure pedestrian safety. On highways, the maximum speed is 90 km/h to optimize fuel efficiency and safety. Speeding violations recorded by telematics devices will result in an immediate review of the driver's contract. Drivers are also required to maintain a safe following distance of at least 3 seconds from the vehicle in front, increasing to 5 seconds in adverse weather conditions such as rain, snow, or fog.

    2. Break Times and Fatigue Management
    Fatigue is a major cause of accidents. Drivers must take a mandatory 45-minute break for every 4.5 hours of driving. This break cannot be split into periods shorter than 15 minutes. During breaks, drivers are encouraged to exit the vehicle and stretch. All breaks must be logged in the LogiSmart Driver App. Failure to log breaks or manipulating log data is a serious offense. Drivers are prohibited from operating the vehicle if they feel drowsy or fatigued, and must contact dispatch immediately to arrange for a replacement or rest period.

    3. Vehicle Maintenance and Pre-Trip Inspection
    Before starting any shift, drivers must perform a comprehensive pre-trip inspection. This includes checking tire pressure, oil levels, coolant, lights, and brakes. Any defects must be reported via the app before the vehicle is moved. The cargo area must be inspected for cleanliness and structural integrity. At the end of the shift, a post-trip inspection is required to identify any issues that may have arisen during operation. The vehicle must be kept clean and presentable at all times, as it represents the LogiSmart brand. Smoking is strictly prohibited inside the vehicle cabin.

    4. Emergency Protocol and Accident Reporting
    In the event of an accident, the driver's first priority is safety. Stop the vehicle immediately in a safe location and activate hazard lights. Check for injuries and call emergency services if necessary. Press the Red Panic Button on the dashboard to alert the LogiSmart Command Center. Do not admit liability or discuss the accident with anyone other than police or LogiSmart representatives. Take photos of the scene, including vehicle damage and road conditions, and upload them to the incident report form in the app.
    """

    metadata = {"source": "policy_v2.pdf", "author": "HQ"}
    
    count = ingestion_service.ingest_text(sample_policy, metadata)
    print(f"✅ Successfully ingested {count} chunks into Production Service.")

        # 4. Verify by Searching
    print("\n--- Verifying Retrieval ---")
    results = vector_db.search("What is the speed limit?")
    for doc in results:
        print(f"Found chunk: {doc.content[:50]}... (Source: {doc.metadata['source']})")


if __name__ == "__main__":
    run_production_ingestion()

    
