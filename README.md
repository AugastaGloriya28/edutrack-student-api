# 📚 EduTrack — Student Database CRUD API

> **EWB Edu Tech Pvt. Ltd. | Internship Project**  
> Python Backend Development — FastAPI + SQLite Student Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🌟 Features

| Feature | Description |
|---|---|
| ✅ **CRUD** | Create, Read, Update (PUT/PATCH), Delete student records |
| 🔍 **Filters** | Search by name, course, date-of-birth range; pagination support |
| 🛡️ **Validation** | Email format, phone format, future-date guard, duplicate detection |
| 🗄️ **Persistence** | SQLite database — data survives server restarts |
| 🤖 **AI Assistant** | Ask natural-language questions powered by local Ollama (optional) |
| 📄 **Auto Docs** | Swagger UI + ReDoc generated automatically by FastAPI |
| 🎨 **Landing Page** | Beautiful HTML landing page at `/` |

---

## 🏗️ Project Structure

```
EduTrack/
├── main.py                  # FastAPI app entry point + landing page
├── seed.py                  # Seed script (8 sample students)
├── requirements.txt         # Python dependencies
├── .gitignore
├── README.md
└── app/
    ├── database.py          # SQLAlchemy engine, session, Base
    ├── models/
    │   └── student.py       # Student ORM model
    ├── schemas/
    │   └── student.py       # Pydantic request/response schemas
    └── routers/
        ├── students.py      # CRUD endpoints
        └── ai_assistant.py  # Optional AI assistant endpoints
```

---

## ⚡ Quick Start

### Prerequisites

- Python **3.10+** installed → [Download](https://python.org/downloads)
- `git` installed → [Download](https://git-scm.com)
- *(Optional for AI)* [Ollama](https://ollama.com) installed

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/edutrack-student-api.git
cd edutrack-student-api
```

### 2️⃣ Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Server

```bash
uvicorn main:app --reload
```

The API is now live at **http://127.0.0.1:8000** 🎉

### 5️⃣ (Optional) Seed Sample Data

```bash
python seed.py
```

This inserts 8 realistic student records so you can test immediately.

---

## 📖 API Documentation

Once the server is running, open:

| Interface | URL |
|---|---|
| 🏠 Landing Page | http://127.0.0.1:8000/ |
| 📄 Swagger UI | http://127.0.0.1:8000/docs |
| 📘 ReDoc | http://127.0.0.1:8000/redoc |

---

## 🔌 API Endpoints

### Students

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/students/` | Create a new student |
| `GET` | `/students/` | List / filter students |
| `GET` | `/students/{id}` | Get a student by ID |
| `PUT` | `/students/{id}` | Replace all student fields |
| `PATCH` | `/students/{id}` | Partially update a student |
| `DELETE` | `/students/{id}` | Delete a student |

### AI Assistant (optional)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ai/ask` | Ask a natural-language question |
| `GET` | `/ai/status` | Check if Ollama is running |

---

## 🧪 Sample API Requests

### Create a Student

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

### List All Students

```bash
curl http://127.0.0.1:8000/students/
```

### Filter Students by Course

```bash
curl "http://127.0.0.1:8000/students/?course=Computer+Science"
```

### Filter by Name + Pagination

```bash
curl "http://127.0.0.1:8000/students/?name=priya&skip=0&limit=5"
```

### Filter Students Born After 2003

```bash
curl "http://127.0.0.1:8000/students/?dob_after=2003-01-01"
```

### Get Student by ID

```bash
curl http://127.0.0.1:8000/students/1
```

### Partially Update a Student

```bash
curl -X PATCH http://127.0.0.1:8000/students/1 \
  -H "Content-Type: application/json" \
  -d '{"course": "M.Tech Data Science"}'
```

### Delete a Student

```bash
curl -X DELETE http://127.0.0.1:8000/students/1
```

---

## 🤖 AI Assistant (Optional — Requires Ollama)

### Setup

```bash
# 1. Install Ollama from https://ollama.com
# 2. Start the Ollama server
ollama serve

# 3. Pull the model (one-time download ~1 GB)
ollama pull llama3.2:1b
```

### Ask a Question

```bash
curl -X POST http://127.0.0.1:8000/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many students are enrolled in Computer Science?"}'
```

**Example Questions**
- *"How many students are there in total?"*
- *"List students born after 2003."*
- *"Who is the youngest student?"*
- *"Which courses are most popular?"*

### Check Ollama Status

```bash
curl http://127.0.0.1:8000/ai/status
```

> **Security Note:** The AI model never executes raw SQL queries. Student data is fetched safely in Python and passed as read-only context to the model.

---

## 📊 Student Record Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Auto | Unique identifier (auto-generated) |
| `name` | string | ✅ | Full name |
| `date_of_birth` | date | ✅ | Format: `YYYY-MM-DD` |
| `email` | string | ✅ | Valid email, must be unique |
| `phone` | string | ❌ | Phone number |
| `course` | string | ❌ | Course / programme name |
| `address` | string | ❌ | Physical address |
| `enrollment_date` | date | ❌ | Format: `YYYY-MM-DD` |
| `created_at` | datetime | Auto | Record creation timestamp |
| `updated_at` | datetime | Auto | Last update timestamp |

---

## 🛡️ Validation & Error Handling

- **422 Unprocessable Entity** — Invalid field values (bad email, future DOB, short phone)
- **404 Not Found** — Student ID does not exist
- **409 Conflict** — Duplicate email address
- **503 Service Unavailable** — Ollama not running (AI endpoint only)

---

## 🧰 Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Language |
| **FastAPI** | 0.115 | Web framework |
| **SQLAlchemy** | 2.0 | ORM + database layer |
| **SQLite** | Built-in | Persistent storage |
| **Pydantic** | 2.9 | Data validation |
| **Uvicorn** | 0.30 | ASGI server |
| **httpx** | 0.27 | Async HTTP (Ollama calls) |
| **Ollama** | Latest | Local AI model runner |

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

*Developed for the EWB Edu Tech Pvt. Ltd. Internship Program | Python Backend Development Track*
