from datetime import date
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import DBPatient, DBPractitioner

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
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
