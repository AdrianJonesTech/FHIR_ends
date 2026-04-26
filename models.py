from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class HumanName(BaseModel):
    """FHIR HumanName component."""
    family: str = Field(..., description="Family name")
    given: List[str] = Field(default_factory=list, description="Given names")


class Patient(BaseModel):
    """Stub FHIR Patient resource (R4 minimal)."""
    resourceType: str = Field("Patient", pattern="^Patient$")
    id: Optional[str] = Field(None, description="Logical ID")
    name: List[HumanName] = Field(..., description="Patient names")
    birthDate: Optional[date] = Field(None, description="Birth date")
    gender: Optional[str] = Field(None, description="male | female | other | unknown")

    class Config:
        # Enable ORM mode for potential DB integration
        from_attributes = True
        # FHIR uses snake_case internally sometimes, but we use camelCase for JSON
        populate_by_name = True
