from datetime import date
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import DBPatient

def seed_data():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Check if we already have data
        if db.query(DBPatient).count() > 0:
            print("Database already has data. Skipping seeding.")
            return

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
        
        db.add_all(patients)
        db.commit()
        print(f"Successfully added {len(patients)} patients.")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
