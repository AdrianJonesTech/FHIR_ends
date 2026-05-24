from fastapi import FastAPI, HTTPException, Path, Depends, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import secrets
import hashlib
import base64
import urllib.parse
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from models import (
    Patient, DBPatient, Practitioner, DBPractitioner,
    Observation, DBObservation, Coverage, ExplanationOfBenefit,
    CapabilityStatement, Bundle, BundleEntry, OperationOutcome, OperationOutcomeIssue
)
from database import engine, Base, get_db

# Create tables
Base.metadata.create_all(bind=engine)

# Blue Button 2.0 Configuration (Sandbox)
BLUEBUTTON_CLIENT_ID = os.getenv("BLUEBUTTON_CLIENT_ID", "")
BLUEBUTTON_CLIENT_SECRET = os.getenv("BLUEBUTTON_CLIENT_SECRET", "")
BLUEBUTTON_AUTH_URL = "https://sandbox.bluebutton.cms.gov/v2/o/authorize"
BLUEBUTTON_TOKEN_URL = "https://sandbox.bluebutton.cms.gov/v2/o/token"
BLUEBUTTON_CALLBACK_URL = "http://localhost:8000/api/oauth/callback/"

# In-memory store for PKCE verifiers and states (use a proper session/cache in production)
oauth_state_store = {}

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
                    "type": "Coverage",
                    "interaction": [
                        {"code": "read"},
                        {"code": "search-type"}
                    ],
                    "searchParam": [
                        {"name": "beneficiary", "type": "reference", "documentation": "The beneficiary of the coverage"}
                    ]
                },
                {
                    "type": "ExplanationOfBenefit",
                    "interaction": [
                        {"code": "read"},
                        {"code": "search-type"}
                    ],
                    "searchParam": [
                        {"name": "patient", "type": "reference", "documentation": "The patient of the EOB"}
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


# OAuth 2.0 Endpoints for Blue Button 2.0 Integration

@app.get("/api/diagnostic")
async def diagnostic():
    """Diagnostic endpoint to check configuration status."""
    return {
        "bluebutton_client_id_set": bool(BLUEBUTTON_CLIENT_ID),
        "bluebutton_client_secret_set": bool(BLUEBUTTON_CLIENT_SECRET),
        "database_url_configured": "postgres" in os.getenv("DATABASE_URL", ""),
        "callback_url": BLUEBUTTON_CALLBACK_URL
    }


@app.get("/api/oauth/login")
async def oauth_login():
    """Initiate Blue Button 2.0 OAuth flow."""
    state = secrets.token_urlsafe(32)
    
    # PKCE Implementation
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('ascii')).digest()
    ).decode('ascii').rstrip('=')
    
    # Store state and verifier to verify them later
    oauth_state_store[state] = {
        "code_verifier": code_verifier,
        "created_at": datetime.now()
    }
    
    params = {
        "response_type": "code",
        "client_id": BLUEBUTTON_CLIENT_ID,
        "redirect_uri": BLUEBUTTON_CALLBACK_URL,
        "state": state,
        "scope": "patient/Patient.rs patient/Coverage.rs patient/ExplanationOfBenefit.rs profile openid",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    auth_url = f"{BLUEBUTTON_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return {"url": auth_url}


@app.get("/api/oauth/callback/")
async def oauth_callback(code: Optional[str] = Query(None), state: Optional[str] = Query(None), error: Optional[str] = Query(None)):
    """Handle OAuth callback and exchange code for access token."""
    if error:
        print(f"OAuth error from provider: {error}")
        return RedirectResponse(url=f"http://localhost:3000/dashboard?status=error&message={urllib.parse.quote(error)}")

    if not code or not state:
        return RedirectResponse(url="http://localhost:3000/dashboard?status=error&message=Missing+required+parameters")

    if state not in oauth_state_store:
        return RedirectResponse(url="http://localhost:3000/dashboard?status=error&message=Invalid+state")
    
    stored_data = oauth_state_store[state]
    code_verifier = stored_data.get("code_verifier")
    
    # Remove state after use
    del oauth_state_store[state]
    
    async with httpx.AsyncClient() as client:
        try:
            # CMS Blue Button 2.0 requires Basic Auth for the token exchange
            # and the code_verifier for PKCE
            response = await client.post(
                BLUEBUTTON_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": BLUEBUTTON_CALLBACK_URL,
                    "code_verifier": code_verifier,
                },
                auth=(BLUEBUTTON_CLIENT_ID, BLUEBUTTON_CLIENT_SECRET)
            )
            
            if response.status_code != 200:
                # Log error and inform frontend
                error_detail = response.text
                print(f"Token exchange failed (Status {response.status_code}): {error_detail}")
                # We can pass more info to the frontend if we want, but for now let's just log it here
                return RedirectResponse(url=f"http://localhost:3000/dashboard?status=error&detail={urllib.parse.quote(error_detail)}")
            
            token_data = response.json()
            # Store token_data for the session (simplistic demo approach)
            # In a real app, this would be tied to a specific user session
            oauth_state_store["current_token"] = token_data.get("access_token")
            oauth_state_store["patient_id"] = token_data.get("patient")
            
            frontend_url = "http://localhost:3000/dashboard?status=connected"
            return RedirectResponse(url=frontend_url)
            
        except Exception as e:
            print(f"OAuth error: {str(e)}")
            return RedirectResponse(url="http://localhost:3000/dashboard?status=error")


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
    # Check if this is a Blue Button patient (starts with -)
    if patient_id.startswith("-") and "current_token" in oauth_state_store:
        async with httpx.AsyncClient() as client:
            try:
                # Fetch from BB2 Sandbox
                bb2_response = await client.get(
                    f"https://sandbox.bluebutton.cms.gov/v2/fhir/Patient/{patient_id}/",
                    headers={"Authorization": f"Bearer {oauth_state_store['current_token']}"}
                )
                if bb2_response.status_code == 200:
                    data = bb2_response.json()
                    # Map BB2 format to our minimal Patient model if necessary
                    return Patient(
                        id=data.get("id"),
                        resourceType="Patient",
                        birthDate=data.get("birthDate"),
                        gender=data.get("gender"),
                        name=[{
                            "family": n.get("family"),
                            "given": n.get("given", [])
                        } for n in data.get("name", [])]
                    )
            except Exception as e:
                print(f"Error fetching from BB2: {e}")

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
    # Check if this is a Blue Button patient
    p_id = patient.replace("Patient/", "") if patient else None
    if p_id and p_id.startswith("-") and "current_token" in oauth_state_store:
        async with httpx.AsyncClient() as client:
            try:
                # BB2 v2 uses ExplanationOfBenefit and Coverage mostly, 
                # but it might have some Observation-like data or we can simulate it.
                # Actually BB2 Sandbox has Observation resources too for some patients.
                bb2_response = await client.get(
                    f"https://sandbox.bluebutton.cms.gov/v2/fhir/Observation/",
                    params={"patient": p_id},
                    headers={"Authorization": f"Bearer {oauth_state_store['current_token']}"}
                )
                if bb2_response.status_code == 200:
                    return Bundle(**bb2_response.json())
            except Exception as e:
                print(f"Error fetching observations from BB2: {e}")

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


@app.get("/fhir/Coverage", response_model=Bundle)
async def search_coverage(
    beneficiary: Optional[str] = Query(None, description="Beneficiary ID"),
    db: Session = Depends(get_db)
) -> Bundle:
    """Search for Coverage resources."""
    p_id = beneficiary.replace("Patient/", "") if beneficiary else None
    if p_id and p_id.startswith("-") and "current_token" in oauth_state_store:
        async with httpx.AsyncClient() as client:
            try:
                bb2_response = await client.get(
                    f"https://sandbox.bluebutton.cms.gov/v2/fhir/Coverage/",
                    params={"beneficiary": p_id},
                    headers={"Authorization": f"Bearer {oauth_state_store['current_token']}"}
                )
                if bb2_response.status_code == 200:
                    return Bundle(**bb2_response.json())
            except Exception as e:
                print(f"Error fetching coverage from BB2: {e}")

    # Local storage doesn't have Coverage yet, return empty bundle
    return Bundle(total=0, entry=[])


@app.get("/fhir/ExplanationOfBenefit", response_model=Bundle)
async def search_eob(
    patient: Optional[str] = Query(None, description="Patient ID"),
    db: Session = Depends(get_db)
) -> Bundle:
    """Search for ExplanationOfBenefit resources."""
    p_id = patient.replace("Patient/", "") if patient else None
    if p_id and p_id.startswith("-") and "current_token" in oauth_state_store:
        async with httpx.AsyncClient() as client:
            try:
                bb2_response = await client.get(
                    f"https://sandbox.bluebutton.cms.gov/v2/fhir/ExplanationOfBenefit/",
                    params={"patient": p_id},
                    headers={"Authorization": f"Bearer {oauth_state_store['current_token']}"}
                )
                if bb2_response.status_code == 200:
                    return Bundle(**bb2_response.json())
            except Exception as e:
                print(f"Error fetching EOB from BB2: {e}")

    # Local storage doesn't have EOB yet, return empty bundle
    return Bundle(total=0, entry=[])


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
