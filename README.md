# 📚 EduTrack — Student Database CRUD API

> **EWB Edu Tech Pvt. Ltd. | Internship Project Assignment**  
> **Python Backend Development — FastAPI + SQLite Student Management System**  
> **Developer:** Augasta Gloriya R ([@AugastaGloriya28](https://github.com/AugastaGloriya28))  
> 📑 **[Read the Official Project Summary Report](PROJECT_SUMMARY_REPORT.md)**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://sqlite.org)
[![Tests](https://img.shields.io/badge/Tests-22%20Passed-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🌟 Features

| Feature | Description |
|---|---|
| ✅ **Full CRUD** | Create, Read, Update (PUT/PATCH), Delete student records |
| 🔍 **Search & Filters** | Search by name, course, date-of-birth range, and pagination support |
| 🛡️ **Strict Validation** | Email RFC format, regex phone format, future-date guard, duplicate detection |
| 🗄️ **ACID Persistence** | SQLite relational database with SQLAlchemy 2.0 ORM |
| 🤖 **Local AI Assistant** | Ask natural-language questions via local Ollama (`llama3.2:1b`) with grounded SQLite context and seamless offline fallback |
| 📊 **Stats Dashboard** | Interactive glassmorphic analytics dashboard with SVG distribution charts at `/stats/dashboard` |
| 📄 **Interactive API Docs**| Auto-generated Swagger UI (`/docs`) and ReDoc (`/redoc`) |
| 🎨 **Landing Page** | Responsive, modern web interface served at `/` |

---

## 🏗️ Project Structure

```
edutrack-student-api/
├── main.py                     # FastAPI application entry point + landing page
├── seed.py                     # Seed script (populates 8 realistic students)
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── runtime.txt                 # Python runtime version
├── render.yaml                 # Deployment configuration
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── PROJECT_SUMMARY_REPORT.md   # Official internship completion report
├── app/
│   ├── database.py             # SQLAlchemy engine, session maker, Base
│   ├── models/
│   │   └── student.py          # Student SQLAlchemy ORM model
│   ├── schemas/
│   │   └── student.py          # Pydantic request / response schemas & validators
│   └── routers/
│       ├── students.py         # Full CRUD endpoints (/students)
│       ├── ai_assistant.py     # Ollama AI integration + grounded fallback (/ai)
│       └── stats.py            # Analytics & visual dashboard (/stats)
└── tests/
    ├── conftest.py             # TestClient & in-memory SQLite fixtures
    ├── test_api.py             # 15 tests covering CRUD, filters, and validations
    ├── test_stats.py           # 2 tests covering stats and dashboard
    └── test_ai.py              # 5 tests covering AI questions and status
```

---

## ⚡ Quick Start

### Prerequisites

- Python **3.10+** installed → [Download](https://python.org/downloads)
- `git` installed → [Download](https://git-scm.com)
- *(Optional for AI)* [Ollama](https://ollama.com) installed (an automatic fallback is built-in if Ollama is offline)

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/AugastaGloriya28/edutrack-student-api.git
cd edutrack-student-api
```

### 2️⃣ Create and Activate a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ (Optional) Seed Sample Data

```bash
python seed.py
```
*Inserts 8 realistic student records with courses, emails, and phone numbers.*

### 5️⃣ Run the Server

```bash
uvicorn main:app --reload
```

The API will be live at **http://127.0.0.1:8000** 🎉

---

## 🧪 Running Automated Tests

Run the complete test suite (22 unit & integration tests):

```bash
pytest -v
```

All 22 tests run against an isolated in-memory SQLite database without modifying persistent data.

---

## 📖 API Documentation & Web Interfaces

When the application is running, open:

| Interface | URL | Description |
|---|---|---|
| 🏠 **Landing Page** | `http://127.0.0.1:8000/` | Web home page with quick links |
| 📄 **Swagger UI** | `http://127.0.0.1:8000/docs` | Interactive OpenAPI documentation & testing |
| 📘 **ReDoc** | `http://127.0.0.1:8000/redoc` | Clean alternate API documentation |
| 📊 **Stats Dashboard**| `http://127.0.0.1:8000/stats/dashboard` | Visual analytics & course distribution charts |

---

## 🔌 API Endpoints Reference

### 👤 Student Management (`/students`)

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `POST` | `/students/` | Create a new student record | `201`, `409`, `422` |
| `GET` | `/students/` | List / filter students (name, course, DOB, pagination) | `200` |
| `GET` | `/students/{id}` | Retrieve a student's profile by ID | `200`, `404` |
| `PUT` | `/students/{id}` | Replace all details of an existing student | `200`, `404`, `409` |
| `PATCH` | `/students/{id}` | Partially update selected fields of a student | `200`, `404`, `409` |
| `DELETE` | `/students/{id}` | Permanently delete a student record | `204`, `404` |

### 🤖 AI Assistant (`/ai`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ai/ask` | Ask natural-language questions (e.g., *"How many students are there?"*, *"List students born after 2005"*) |
| `GET` | `/ai/status` | Check local Ollama health and available models |

### 📊 Analytics & Reporting (`/stats`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/stats/summary` | JSON summary of totals, course counts, and age groups |
| `GET` | `/stats/dashboard`| Interactive HTML dashboard with charts |

---

## 💻 Sample API Requests (cURL)

### 1. Create a Student
```bash
curl -X POST http://127.0.0.1:8000/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Sharma",
    "date_of_birth": "2003-07-15",
    "email": "priya.sharma@example.com",
    "phone": "+91 98765 43210",
    "course": "B.Tech Computer Science",
    "address": "12, Rose Garden, Bengaluru",
    "enrollment_date": "2022-08-01"
  }'
```

### 2. List All Students (with Course Filter)
```bash
curl "http://127.0.0.1:8000/students/?course=Computer+Science"
```

### 3. Filter Students Born After 2003
```bash
curl "http://127.0.0.1:8000/students/?dob_after=2003-01-01"
```

### 4. Partial Update (PATCH)
```bash
curl -X PATCH http://127.0.0.1:8000/students/1 \
  -H "Content-Type: application/json" \
  -d '{"course": "M.Tech Data Science"}'
```

### 5. Ask the AI Assistant
```bash
curl -X POST http://127.0.0.1:8000/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many students are there?"}'
```

---

## 🔒 Security & AI Grounding

1. **No Raw SQL Execution:** The AI model never constructs or executes SQL commands directly. All data is retrieved safely via SQLAlchemy ORM.
2. **Context Window Injection:** Retrieved records are serialized to structured JSON and provided as read-only grounding context in the prompt.
3. **Deterministic Fallback:** If Ollama is not running on the host machine, the `/ai/ask` endpoint automatically routes questions to an internal SQLite-grounded answering engine so requests never fail with 503.
4. **Input Sanitization:** Email validation, date-of-birth boundaries (no future dates), and phone regex verification protect against malformed data.

---

## 📊 Student Record Schema

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | `Integer` | Primary Key, Auto-increment | Unique student ID |
| `name` | `String(120)` | `NOT NULL`, Non-empty | Full name |
| `date_of_birth` | `Date` | `NOT NULL`, Past date only | Date of birth (`YYYY-MM-DD`) |
| `email` | `String(180)` | `NOT NULL`, Unique | Valid email address |
| `phone` | `String(20)` | Optional | Validated phone number |
| `course` | `String(120)` | Optional | Enrolled course / major |
| `address` | `String(300)` | Optional | Mailing address |
| `enrollment_date` | `Date` | Optional | Date of admission (`YYYY-MM-DD`) |
| `created_at` | `DateTime` | Auto | Timestamp of record creation |
| `updated_at` | `DateTime` | Auto | Timestamp of last modification |

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

**Developed for the EWB Edu Tech Pvt. Ltd. Internship Program**  
*Python Backend Development Track*
