from pydantic import BaseModel


class SoilRecord(BaseModel):
    parameter_name: str
    unit: str
    low_below: str
    high_above: str
    threshold_standard: str
    measurement_basis: str
    what_it_means: str
    source_url: str
