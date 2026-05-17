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


class DBPractitioner(Base):
    __tablename__ = "practitioners"

    id = Column(String, primary_key=True, index=True)
    resourceType = Column(String, default="Practitioner")
    gender = Column(String, nullable=True)
    name = Column(JSON, nullable=False)


class HumanName(BaseModel):
    """FHIR HumanName component."""
    family: Optional[str] = Field(None, description="Family name")
    given: List[str] = Field(default_factory=list, description="Given names")


class Patient(BaseModel):
    """Stub FHIR Patient resource (R4 minimal)."""
    resourceType: str = Field("Patient", pattern="^Patient$")
    id: Optional[str] = Field(None, description="Logical ID")
    name: List[HumanName] = Field(default_factory=list, description="Patient names")
    birthDate: Optional[date] = Field(None, description="Birth date")
    gender: Optional[str] = Field(None, description="male | female | other | unknown")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class Practitioner(BaseModel):
    """Stub FHIR Practitioner resource (R4 minimal)."""
    resourceType: str = Field("Practitioner", pattern="^Practitioner$")
    id: Optional[str] = Field(None, description="Logical ID")
    name: List[HumanName] = Field(default_factory=list, description="Practitioner names")
    gender: Optional[str] = Field(None, description="male | female | other | unknown")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class BundleEntry(BaseModel):
    """FHIR Bundle Entry."""
    fullUrl: Optional[str] = None
    resource: Optional[dict] = None


class Bundle(BaseModel):
    """FHIR Bundle resource."""
    resourceType: str = Field("Bundle", pattern="^Bundle$")
    type: str = Field("searchset")
    total: Optional[int] = None
    entry: List[BundleEntry] = Field(default_factory=list)


class CapabilityStatement(BaseModel):
    """Minimal FHIR CapabilityStatement."""
    resourceType: str = Field("CapabilityStatement", pattern="^CapabilityStatement$")
    status: str = "active"
    date: date
    kind: str = "instance"
    fhirVersion: str = "4.0.1"
    format: List[str] = ["json"]
    rest: List[dict] = []


class OperationOutcomeIssue(BaseModel):
    """FHIR OperationOutcome Issue."""
    severity: str
    code: str
    diagnostics: Optional[str] = None


class OperationOutcome(BaseModel):
    """FHIR OperationOutcome resource."""
    resourceType: str = Field("OperationOutcome", pattern="^OperationOutcome$")
    issue: List[OperationOutcomeIssue]
