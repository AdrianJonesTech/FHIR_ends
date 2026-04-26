from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import RedirectResponse
from typing import List
from models import Patient

app = FastAPI(
    title="Digital Healthcare FHIR Backend Stub",
    description="Stub endpoints for FHIR Patient integration",
    version="0.1.0"
)

# In-memory DB stub (replace with SQLAlchemy/Postgres + FHIR server like HAPI FHIR)
patients_db: List[Patient] = []


@app.get("/")
async def root():
    """Redirect to interactive docs."""
    return RedirectResponse(url="/docs")


@app.post("/fhir/Patient", response_model=Patient, status_code=201)
async def create_patient(patient: Patient) -> Patient:
    """Create a new Patient resource."""
    if patient.id:
        # Check for duplicate ID
        if any(p.id == patient.id for p in patients_db):
            raise HTTPException(status_code=409, detail="Patient with this ID already exists")
    else:
        # Auto-generate ID stub
        patient.id = f"patient-{len(patients_db) + 1}"
    patients_db.append(patient)
    return patient


@app.get("/fhir/Patient", response_model=List[Patient])
async def search_patients() -> List[Patient]:
    """Search/retrieve all Patients (add query params for _search later)."""
    return patients_db


@app.get("/fhir/Patient/{patient_id}", response_model=Patient)
async def read_patient(patient_id: str = Path(..., description="Logical ID")) -> Patient:
    """Retrieve a Patient by ID."""
    for patient in patients_db:
        if patient.id == patient_id:
            return patient
    raise HTTPException(status_code=404, detail="Patient not found")


@app.put("/fhir/Patient/{patient_id}", response_model=Patient)
async def update_patient(
    patient: Patient,
    patient_id: str = Path(..., description="Logical ID")
) -> Patient:
    """Update a Patient resource."""
    if patient.id and patient.id != patient_id:
        raise HTTPException(status_code=400, detail="ID mismatch")
    patient.id = patient_id
    for i, p in enumerate(patients_db):
        if p.id == patient_id:
            patients_db[i] = patient
            return patient
    raise HTTPException(status_code=404, detail="Patient not found")


@app.delete("/fhir/Patient/{patient_id}", status_code=204)
async def delete_patient(patient_id: str = Path(..., description="Logical ID")):
    """Delete a Patient resource."""
    for i, patient in enumerate(patients_db):
        if patient.id == patient_id:
            patients_db.pop(i)
            return None
    raise HTTPException(status_code=404, detail="Patient not found")
