from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Date, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class DBPatient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    resourceType = Column(String, default="Patient")
    birthDate = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    name = Column(JSON, nullable=False)

    observations = relationship("DBObservation", back_populates="subject")


class DBPractitioner(Base):
    __tablename__ = "practitioners"

    id = Column(String, primary_key=True, index=True)
    resourceType = Column(String, default="Practitioner")
    gender = Column(String, nullable=True)
    name = Column(JSON, nullable=False)


class DBObservation(Base):
    __tablename__ = "observations"

    id = Column(String, primary_key=True, index=True)
    resourceType = Column(String, default="Observation")
    status = Column(String, nullable=False)
    category = Column(JSON, nullable=True)
    code = Column(JSON, nullable=False)
    subject_id = Column(String, ForeignKey("patients.id"))
    effectiveDateTime = Column(String, nullable=True)
    valueQuantity = Column(JSON, nullable=True)
    valueCodeableConcept = Column(JSON, nullable=True)
    valueString = Column(String, nullable=True)

    subject = relationship("DBPatient", back_populates="observations")


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


class Observation(BaseModel):
    """Stub FHIR Observation resource (R4 minimal)."""
    resourceType: str = Field("Observation", pattern="^Observation$")
    id: Optional[str] = Field(None, description="Logical ID")
    status: str = Field(..., description="registered | preliminary | final | amended +")
    category: Optional[List[dict]] = Field(None, description="Classification of type of observation")
    code: dict = Field(..., description="Type of observation (code / type)")
    subject: dict = Field(..., description="Who the observation is about")
    effectiveDateTime: Optional[str] = Field(None, description="Clinically relevant time/time-period for observation")
    valueQuantity: Optional[dict] = None
    valueCodeableConcept: Optional[dict] = None
    valueString: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class Coverage(BaseModel):
    """Stub FHIR Coverage resource."""
    resourceType: str = Field("Coverage", pattern="^Coverage$")
    id: Optional[str] = None
    status: str
    type: Optional[dict] = None
    subscriber: Optional[dict] = None
    beneficiary: dict
    period: Optional[dict] = None
    payor: List[dict]


class ExplanationOfBenefit(BaseModel):
    """Stub FHIR ExplanationOfBenefit resource."""
    resourceType: str = Field("ExplanationOfBenefit", pattern="^ExplanationOfBenefit$")
    id: Optional[str] = None
    status: str
    type: dict
    use: str
    patient: dict
    created: str
    insurer: dict
    provider: dict
    outcome: str
    total: Optional[List[dict]] = None
