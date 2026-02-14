from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator

# Define allowed values for strict typing
CongestionEnum = Literal["LOW", "HIGH", "UNKNOWN"]

class TrafficUpdate(BaseModel):
    segment_id: str
    
    # Semantic check: Speed cannot be negative, and >200 is likely an error
    current_speed: float = Field(ge=0, le=200, description="Speed in km/h")
    
    # Optional field that we will enforce via logic
    congestion_level: Optional[CongestionEnum] = None

    @model_validator(mode='after')
    def infer_congestion_if_missing(self):
        """
        Business Logic / Imputation Layer:
        If the API fails to provide congestion level (returns None),
        we infer it deterministically from the speed.
        This prevents 'null' pollution in the LLM context.
        """
        if self.congestion_level is None:
            # Logic: If speed is below 20km/h, it's definitely congested
            if self.current_speed < 20:
                self.congestion_level = "HIGH"
            else:
                self.congestion_level = "LOW"
        return self

    @model_validator(mode='after')
    def validate_urban_logic(self):
        """
        Contextual Semantic Check:
        If the segment ID indicates an urban area, speeds > 90 are suspicious.
        """
        if "urban" in self.segment_id and self.current_speed > 90:
             raise ValueError(f"Speed {self.current_speed} is physically impossible for urban segment")
        return self