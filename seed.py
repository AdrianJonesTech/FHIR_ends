from datetime import date
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import DBPatient, DBPractitioner, DBObservation

def seed_data():
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        print("Seeding database...")
        patients = [
            DBPatient(
                id="patient-1",
                resourceType="Patient",
                birthDate=date(1980, 5, 12),
                gender="male",
                name=[{"family": "Smith", "given": ["John", "Jacob"]}]
            ),
            DBPatient(
                id="patient-2",
                resourceType="Patient",
                birthDate=date(1992, 8, 24),
                gender="female",
                name=[{"family": "Doe", "given": ["Jane"]}]
            ),
            DBPatient(
                id="patient-3",
                resourceType="Patient",
                birthDate=date(1955, 11, 3),
                gender="other",
                name=[{"family": "Jones", "given": ["Alex"]}]
            ),
            DBPatient(
                id="patient-4",
                resourceType="Patient",
                birthDate=date(2000, 1, 1),
                gender="male",
                name=[{"family": "Smith", "given": ["Robert"]}]
            ),
            DBPatient(
                id="patient-5",
                resourceType="Patient",
                birthDate=date(1985, 6, 15),
                gender="female",
                name=[{"family": "Johnson", "given": ["Emily"]}]
            ),
            # Blue Button 2.0 Synthetic Beneficiaries
            DBPatient(
                id="-20140000000001",
                resourceType="Patient",
                birthDate=date(1970, 1, 1),
                gender="male",
                name=[{"family": "Golden", "given": ["Bene"]}]
            ),
            DBPatient(
                id="-20140000000002",
                resourceType="Patient",
                birthDate=date(1982, 3, 24),
                gender="female",
                name=[{"family": "Green", "given": ["Bene"]}]
            ),
            DBPatient(
                id="-20140000000003",
                resourceType="Patient",
                birthDate=date(1995, 11, 12),
                gender="other",
                name=[{"family": "Blue", "given": ["Bene"]}]
            )
        ]
        
        added_patients = 0
        for p in patients:
            if not db.query(DBPatient).filter(DBPatient.id == p.id).first():
                db.add(p)
                added_patients += 1
        
        db.commit()
        if added_patients > 0:
            print(f"Successfully added {added_patients} new patients.")
        else:
            print("No new patients to add.")

        practitioners = [
            DBPractitioner(
                id="practitioner-1",
                resourceType="Practitioner",
                gender="female",
                name=[{"family": "Wilson", "given": ["Alice"]}]
            ),
            DBPractitioner(
                id="practitioner-2",
                resourceType="Practitioner",
                gender="male",
                name=[{"family": "Brown", "given": ["Bob"]}]
            )
        ]
        
        added_practitioners = 0
        for p in practitioners:
            if not db.query(DBPractitioner).filter(DBPractitioner.id == p.id).first():
                db.add(p)
                added_practitioners += 1
        
        db.commit()
        if added_practitioners > 0:
            print(f"Successfully added {added_practitioners} new practitioners.")
        else:
            print("No new practitioners to add.")

        observations = [
            # Observations for patient-1 (John Smith)
            DBObservation(
                id="obs-1",
                status="final",
                category=[{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
                code={"coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood Pressure"}]},
                subject_id="patient-1",
                effectiveDateTime="2023-10-01T10:00:00Z",
                valueString="120/80 mmHg"
            ),
            DBObservation(
                id="obs-2",
                status="final",
                category=[{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
                code={"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
                subject_id="patient-1",
                effectiveDateTime="2023-10-01T10:05:00Z",
                valueQuantity={"value": 72, "unit": "bpm", "system": "http://unitsofmeasure.org", "code": "/min"}
            ),
            # Observations for patient-2 (Jane Doe)
            DBObservation(
                id="obs-3",
                status="final",
                category=[{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
                code={"coding": [{"system": "http://loinc.org", "code": "8302-2", "display": "Body Height"}]},
                subject_id="patient-2",
                effectiveDateTime="2023-09-15T09:30:00Z",
                valueQuantity={"value": 165, "unit": "cm", "system": "http://unitsofmeasure.org", "code": "cm"}
            ),
            DBObservation(
                id="obs-4",
                status="final",
                category=[{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]}],
                code={"coding": [{"system": "http://loinc.org", "code": "2339-0", "display": "Glucose [Mass/volume] in Blood"}]},
                subject_id="patient-2",
                effectiveDateTime="2023-09-15T09:45:00Z",
                valueQuantity={"value": 95, "unit": "mg/dL", "system": "http://unitsofmeasure.org", "code": "mg/dL"}
            )
        ]

        added_observations = 0
        for o in observations:
            if not db.query(DBObservation).filter(DBObservation.id == o.id).first():
                db.add(o)
                added_observations += 1
        
        db.commit()
        if added_observations > 0:
            print(f"Successfully added {added_observations} new observations.")
        else:
            print("No new observations to add.")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
