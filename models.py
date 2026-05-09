from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


from sqlalchemy import Column, String, Date, JSON
from database import Base

class DBPatient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    resourceType = Column(String, default="Patient")
    birthDate = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    name = Column(JSON, nullable=False)

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

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
