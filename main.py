from fastapi import FastAPI, HTTPException, Path, Depends
from fastapi.responses import RedirectResponse
from typing import List
from sqlalchemy.orm import Session
from models import Patient, DBPatient
from database import engine, Base, get_db

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Healthcare FHIR Backend Stub",
    description="Stub endpoints for FHIR Patient integration",
    version="0.1.0"
)


@app.get("/")
async def root():
    """Redirect to interactive docs."""
    return RedirectResponse(url="/docs")


@app.post("/fhir/Patient", response_model=Patient, status_code=201)
async def create_patient(patient: Patient, db: Session = Depends(get_db)) -> Patient:
    """Create a new Patient resource."""
    if patient.id:
        db_patient = db.query(DBPatient).filter(DBPatient.id == patient.id).first()
        if db_patient:
            raise HTTPException(status_code=409, detail="Patient with this ID already exists")
    else:
        # Auto-generate ID stub
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


@app.get("/fhir/Patient", response_model=List[Patient])
async def search_patients(db: Session = Depends(get_db)) -> List[Patient]:
    """Search/retrieve all Patients (add query params for _search later)."""
    db_patients = db.query(DBPatient).all()
    # Convert DB models to Pydantic models
    return [Patient.model_validate(p) for p in db_patients]


@app.get("/fhir/Patient/{patient_id}", response_model=Patient)
async def read_patient(
    patient_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
) -> Patient:
    """Retrieve a Patient by ID."""
    db_patient = db.query(DBPatient).filter(DBPatient.id == patient_id).first()
    if db_patient:
        return Patient.model_validate(db_patient)
    raise HTTPException(status_code=404, detail="Patient not found")


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
        raise HTTPException(status_code=404, detail="Patient not found")

    db_patient.birthDate = patient.birthDate
    db_patient.gender = patient.gender
    db_patient.name = [n.model_dump() for n in patient.name]

    db.commit()
    db.refresh(db_patient)
    return Patient.model_validate(db_patient)


@app.delete("/fhir/Patient/{patient_id}", status_code=204)
async def delete_patient(
    patient_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
):
    """Delete a Patient resource."""
    db_patient = db.query(DBPatient).filter(DBPatient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(db_patient)
    db.commit()
    return None
