from fastapi import FastAPI, HTTPException, Path, Depends, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from models import (
    Patient, DBPatient, Practitioner, DBPractitioner,
    Observation, DBObservation,
    CapabilityStatement, Bundle, BundleEntry, OperationOutcome, OperationOutcomeIssue
)
from database import engine, Base, get_db

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Healthcare FHIR Backend Stub",
    description="Stub endpoints for FHIR Patient and Practitioner integration",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Redirect to interactive docs."""
    return RedirectResponse(url="/docs")


@app.get("/fhir/metadata", response_model=CapabilityStatement)
async def get_metadata() -> CapabilityStatement:
    """Retrieve the FHIR CapabilityStatement."""
    return CapabilityStatement(
        date=datetime.now().date(),
        rest=[{
            "mode": "server",
            "resource": [
                {
                    "type": "Patient",
                    "interaction": [
                        {"code": "read"},
                        {"code": "update"},
                        {"code": "delete"},
                        {"code": "create"},
                        {"code": "search-type"}
                    ],
                    "searchParam": [
                        {"name": "name", "type": "string", "documentation": "Search by any name component"},
                        {"name": "family", "type": "string", "documentation": "Search by family name"},
                        {"name": "given", "type": "string", "documentation": "Search by given name"},
                        {"name": "gender", "type": "token", "documentation": "Search by gender"}
                    ]
                },
                {
                    "type": "Observation",
                    "interaction": [
                        {"code": "read"},
                        {"code": "search-type"}
                    ],
                    "searchParam": [
                        {"name": "patient", "type": "reference", "documentation": "The subject that the observation is about"},
                        {"name": "category", "type": "token", "documentation": "The category of the observation"}
                    ]
                },
                {
                    "type": "Practitioner",
                    "interaction": [
                        {"code": "read"},
                        {"code": "update"},
                        {"code": "delete"},
                        {"code": "create"},
                        {"code": "search-type"}
                    ]
                }
            ]
        }]
    )


def fhir_error(status_code: int, severity: str, code: str, diagnostics: str):
    """Return a FHIR-compliant OperationOutcome error response."""
    outcome = OperationOutcome(
        issue=[OperationOutcomeIssue(severity=severity, code=code, diagnostics=diagnostics)]
    )
    return JSONResponse(status_code=status_code, content=outcome.model_dump())


@app.post("/fhir/Patient", response_model=Patient, status_code=201)
async def create_patient(patient: Patient, db: Session = Depends(get_db)):
    """Create a new Patient resource."""
    if patient.id:
        db_patient = db.query(DBPatient).filter(DBPatient.id == patient.id).first()
        if db_patient:
            return fhir_error(409, "error", "duplicate", f"Patient with ID {patient.id} already exists")
    else:
        db_count = db.query(DBPatient).count()
        patient.id = f"patient-{db_count + 1}"

    new_patient = DBPatient(
        id=patient.id,
        resourceType=patient.resourceType,
        birthDate=patient.birthDate,
        gender=patient.gender,
        name=[n.model_dump() for n in patient.name]
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return patient


@app.get("/fhir/Patient", response_model=Bundle)
async def search_patients(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    given: Optional[str] = Query(None),
    gender: Optional[str] = Query(None)
) -> Bundle:
    """Search Patients using standard FHIR parameters."""
    query = db.query(DBPatient)

    if gender:
        query = query.filter(DBPatient.gender == gender.lower())

    # Fetch all and filter in Python for demo simplicity
    db_patients = query.all()
    results = [Patient.model_validate(p) for p in db_patients]

    if name:
        name = name.lower()
        results = [
            p for p in results 
            if any(name in (n.family or "").lower() for n in p.name) or 
               any(any(name in g.lower() for g in n.given) for n in p.name)
        ]
    
    if family:
        family = family.lower()
        results = [p for p in results if any(family in (n.family or "").lower() for n in p.name)]

    if given:
        given = given.lower()
        results = [p for p in results if any(any(given in g.lower() for g in n.given) for n in p.name)]

    entries = [
        BundleEntry(resource=p.model_dump(exclude_none=True), fullUrl=f"/fhir/Patient/{p.id}") 
        for p in results
    ]
    return Bundle(total=len(results), entry=entries)


@app.get("/fhir/Patient/{patient_id}", response_model=Patient)
async def read_patient(
    patient_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
) -> Patient:
    """Retrieve a Patient by ID."""
    db_patient = db.query(DBPatient).filter(DBPatient.id == patient_id).first()
    if db_patient:
        return Patient.model_validate(db_patient)
    return fhir_error(404, "error", "not-found", f"Patient {patient_id} not found")


@app.put("/fhir/Patient/{patient_id}", response_model=Patient)
async def update_patient(
    patient: Patient,
    patient_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
) -> Patient:
    """Update a Patient resource."""
    if patient.id and patient.id != patient_id:
        raise HTTPException(status_code=400, detail="ID mismatch")

    db_patient = db.query(DBPatient).filter(DBPatient.id == patient_id).first()
    if not db_patient:
        return fhir_error(404, "error", "not-found", f"Patient {patient_id} not found")

    db_patient.birthDate = patient.birthDate
    db_patient.gender = patient.gender
    db_patient.name = [n.model_dump() for n in patient.name]

    db.commit()
    db.refresh(db_patient)
    return Patient.model_validate(db_patient)


@app.get("/fhir/Observation", response_model=Bundle)
async def search_observations(
    patient: Optional[str] = Query(None, description="Patient ID (e.g. Patient/patient-1 or patient-1)"),
    category: Optional[str] = Query(None, description="Search by category code (e.g. vital-signs)"),
    db: Session = Depends(get_db)
) -> Bundle:
    """Search for Observation resources."""
    query = db.query(DBObservation)

    if patient:
        # Handle both "patient-1" and "Patient/patient-1"
        p_id = patient.replace("Patient/", "")
        query = query.filter(DBObservation.subject_id == p_id)

    observations = query.all()

    # Filter by category code in the JSON category field
    if category:
        filtered_obs = []
        for obs in observations:
            if obs.category:
                match = False
                for cat in obs.category:
                    for coding in cat.get("coding", []):
                        if coding.get("code") == category:
                            match = True
                            break
                    if match:
                        break
                if match:
                    filtered_obs.append(obs)
        observations = filtered_obs
    
    entries = []
    for obs in observations:
        # Convert DB model to FHIR-like dict
        obs_dict = {
            "resourceType": "Observation",
            "id": obs.id,
            "status": obs.status,
            "category": obs.category,
            "code": obs.code,
            "subject": {"reference": f"Patient/{obs.subject_id}"},
            "effectiveDateTime": obs.effectiveDateTime,
            "valueQuantity": obs.valueQuantity,
            "valueCodeableConcept": obs.valueCodeableConcept,
            "valueString": obs.valueString
        }
        entries.append(BundleEntry(
            fullUrl=f"http://localhost:8000/fhir/Observation/{obs.id}",
            resource=obs_dict
        ))

    return Bundle(
        total=len(entries),
        entry=entries
    )


@app.get("/fhir/Observation/{observation_id}", response_model=Observation)
async def read_observation(
    observation_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
) -> Observation:
    """Retrieve an Observation by ID."""
    obs = db.query(DBObservation).filter(DBObservation.id == observation_id).first()
    if obs:
        return Observation(
            id=obs.id,
            status=obs.status,
            category=obs.category,
            code=obs.code,
            subject={"reference": f"Patient/{obs.subject_id}"},
            effectiveDateTime=obs.effectiveDateTime,
            valueQuantity=obs.valueQuantity,
            valueCodeableConcept=obs.valueCodeableConcept,
            valueString=obs.valueString
        )
    return fhir_error(404, "error", "not-found", f"Observation {observation_id} not found")


@app.delete("/fhir/Patient/{patient_id}", status_code=204)
async def delete_patient(
    patient_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
):
    """Delete a Patient resource."""
    db_patient = db.query(DBPatient).filter(DBPatient.id == patient_id).first()
    if not db_patient:
        return fhir_error(404, "error", "not-found", f"Patient {patient_id} not found")

    db.delete(db_patient)
    db.commit()
    return None


# Practitioner endpoints

@app.post("/fhir/Practitioner", response_model=Practitioner, status_code=201)
async def create_practitioner(practitioner: Practitioner, db: Session = Depends(get_db)):
    """Create a new Practitioner resource."""
    if practitioner.id:
        db_practitioner = db.query(DBPractitioner).filter(DBPractitioner.id == practitioner.id).first()
        if db_practitioner:
            return fhir_error(409, "error", "duplicate", f"Practitioner with ID {practitioner.id} already exists")
    else:
        db_count = db.query(DBPractitioner).count()
        practitioner.id = f"practitioner-{db_count + 1}"

    new_practitioner = DBPractitioner(
        id=practitioner.id,
        resourceType=practitioner.resourceType,
        gender=practitioner.gender,
        name=[n.model_dump() for n in practitioner.name]
    )
    db.add(new_practitioner)
    db.commit()
    db.refresh(new_practitioner)
    return practitioner


@app.get("/fhir/Practitioner", response_model=Bundle)
async def search_practitioners(db: Session = Depends(get_db)) -> Bundle:
    """Search/retrieve all Practitioners."""
    db_practitioners = db.query(DBPractitioner).all()
    results = [Practitioner.model_validate(p) for p in db_practitioners]
    entries = [
        BundleEntry(resource=p.model_dump(exclude_none=True), fullUrl=f"/fhir/Practitioner/{p.id}") 
        for p in results
    ]
    return Bundle(total=len(results), entry=entries)


@app.get("/fhir/Practitioner/{practitioner_id}", response_model=Practitioner)
async def read_practitioner(
    practitioner_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
) -> Practitioner:
    """Retrieve a Practitioner by ID."""
    db_practitioner = db.query(DBPractitioner).filter(DBPractitioner.id == practitioner_id).first()
    if db_practitioner:
        return Practitioner.model_validate(db_practitioner)
    return fhir_error(404, "error", "not-found", f"Practitioner {practitioner_id} not found")


@app.put("/fhir/Practitioner/{practitioner_id}", response_model=Practitioner)
async def update_practitioner(
    practitioner: Practitioner,
    practitioner_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
) -> Practitioner:
    """Update a Practitioner resource."""
    if practitioner.id and practitioner.id != practitioner_id:
        raise HTTPException(status_code=400, detail="ID mismatch")

    db_practitioner = db.query(DBPractitioner).filter(DBPractitioner.id == practitioner_id).first()
    if not db_practitioner:
        return fhir_error(404, "error", "not-found", f"Practitioner {practitioner_id} not found")

    db_practitioner.gender = practitioner.gender
    db_practitioner.name = [n.model_dump() for n in practitioner.name]

    db.commit()
    db.refresh(db_practitioner)
    return Practitioner.model_validate(db_practitioner)


@app.delete("/fhir/Practitioner/{practitioner_id}", status_code=204)
async def delete_practitioner(
    practitioner_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
):
    """Delete a Practitioner resource."""
    db_practitioner = db.query(DBPractitioner).filter(DBPractitioner.id == practitioner_id).first()
    if not db_practitioner:
        return fhir_error(404, "error", "not-found", f"Practitioner {practitioner_id} not found")

    db.delete(db_practitioner)
    db.commit()
    return None
