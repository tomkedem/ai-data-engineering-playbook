# src/models.py
from dataclasses import dataclass
from typing import List, Literal, Dict, Any

@dataclass
class ShipmentArtifact:
    """Represents a single piece of evidence (text or image)."""
    content_path: str   # Path to image file or text file
    artifact_type: Literal['ocr_text', 'damage_photo', 'delivery_slip']
    metadata: Dict[str, Any]

@dataclass
class ShipmentCase:
    """The aggregate unit: A collection of artifacts tied to one shipment."""
    shipment_id: str
    customer_id: str
    artifacts: List[ShipmentArtifact]
