from fastapi import FastAPI, HTTPException, Path, Depends
from fastapi.responses import RedirectResponse
from typing import List
from sqlalchemy.orm import Session
from models import Patient, DBPatient, Practitioner, DBPractitioner
from database import engine, Base, get_db

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Digital Healthcare FHIR Backend Stub",
    description="Stub endpoints for FHIR Patient and Practitioner integration",
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
    """Search/retrieve all Patients."""
    db_patients = db.query(DBPatient).all()
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


# Practitioner endpoints

@app.post("/fhir/Practitioner", response_model=Practitioner, status_code=201)
async def create_practitioner(practitioner: Practitioner, db: Session = Depends(get_db)) -> Practitioner:
    """Create a new Practitioner resource."""
    if practitioner.id:
        db_practitioner = db.query(DBPractitioner).filter(DBPractitioner.id == practitioner.id).first()
        if db_practitioner:
            raise HTTPException(status_code=409, detail="Practitioner with this ID already exists")
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


@app.get("/fhir/Practitioner", response_model=List[Practitioner])
async def search_practitioners(db: Session = Depends(get_db)) -> List[Practitioner]:
    """Search/retrieve all Practitioners."""
    return [Practitioner.model_validate(p) for p in db.query(DBPractitioner).all()]


@app.get("/fhir/Practitioner/{practitioner_id}", response_model=Practitioner)
async def read_practitioner(
    practitioner_id: str = Path(..., description="Logical ID"),
    db: Session = Depends(get_db)
) -> Practitioner:
    """Retrieve a Practitioner by ID."""
    db_practitioner = db.query(DBPractitioner).filter(DBPractitioner.id == practitioner_id).first()
    if db_practitioner:
        return Practitioner.model_validate(db_practitioner)
    raise HTTPException(status_code=404, detail="Practitioner not found")


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
        raise HTTPException(status_code=404, detail="Practitioner not found")

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
        raise HTTPException(status_code=404, detail="Practitioner not found")

    db.delete(db_practitioner)
    db.commit()
    return None
