"""
Seed script — populates the database with realistic sample student records.

Usage:
    python seed.py
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models.student import Student
from datetime import date

SAMPLE_STUDENTS = [
    {
        "name": "Priya Sharma",
        "date_of_birth": date(2003, 7, 15),
        "email": "priya.sharma@example.com",
        "phone": "+91 98765 43210",
        "course": "B.Tech Computer Science",
        "address": "12, Rose Garden, Bengaluru, Karnataka",
        "enrollment_date": date(2022, 8, 1),
    },
    {
        "name": "Arjun Mehta",
        "date_of_birth": date(2002, 3, 22),
        "email": "arjun.mehta@example.com",
        "phone": "+91 91234 56789",
        "course": "B.Tech Electronics",
        "address": "45, MG Road, Mumbai, Maharashtra",
        "enrollment_date": date(2021, 7, 15),
    },
    {
        "name": "Sneha Reddy",
        "date_of_birth": date(2004, 11, 5),
        "email": "sneha.reddy@example.com",
        "phone": "+91 87654 32100",
        "course": "BCA",
        "address": "8, Hitech City, Hyderabad, Telangana",
        "enrollment_date": date(2023, 6, 10),
    },
    {
        "name": "Vikram Nair",
        "date_of_birth": date(2001, 9, 18),
        "email": "vikram.nair@example.com",
        "phone": "+91 99887 76655",
        "course": "M.Tech Data Science",
        "address": "22, Infopark, Kochi, Kerala",
        "enrollment_date": date(2022, 1, 20),
    },
    {
        "name": "Ananya Joshi",
        "date_of_birth": date(2003, 4, 30),
        "email": "ananya.joshi@example.com",
        "phone": "+91 70000 11111",
        "course": "B.Tech Computer Science",
        "address": "3, Satellite Road, Ahmedabad, Gujarat",
        "enrollment_date": date(2022, 8, 1),
    },
    {
        "name": "Rohit Kapoor",
        "date_of_birth": date(2005, 1, 12),
        "email": "rohit.kapoor@example.com",
        "phone": "+91 88888 99999",
        "course": "BBA",
        "address": "71, Connaught Place, New Delhi",
        "enrollment_date": date(2024, 7, 5),
    },
    {
        "name": "Deepika Pillai",
        "date_of_birth": date(2002, 6, 8),
        "email": "deepika.pillai@example.com",
        "phone": "+91 76543 21098",
        "course": "MBA",
        "address": "56, Anna Nagar, Chennai, Tamil Nadu",
        "enrollment_date": date(2021, 9, 1),
    },
    {
        "name": "Aarav Gupta",
        "date_of_birth": date(2006, 2, 25),
        "email": "aarav.gupta@example.com",
        "phone": None,
        "course": "B.Sc. Mathematics",
        "address": "9, Civil Lines, Jaipur, Rajasthan",
        "enrollment_date": date(2024, 7, 22),
    },
]


def seed():
    init_db()
    db = SessionLocal()
    added = 0
    skipped = 0
    try:
        for data in SAMPLE_STUDENTS:
            exists = db.query(Student).filter(Student.email == data["email"]).first()
            if exists:
                skipped += 1
                continue
            db.add(Student(**data))
            added += 1
        db.commit()
        print(f"[OK] Seed complete: {added} students added, {skipped} skipped (already existed).")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
