from pydantic import BaseModel, Field

class SoilRecord(BaseModel):
    sample_id: int
    farmer_name: str
    location: str
    soil_type: str
    ph: float = Field(..., ge=0.0, le=14.0)
    nitrogen: float
    phosphorus: float
    potassium: float