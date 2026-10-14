"""
╔══════════════════════════════════════════════════════════════════╗
║         EduTrack — Students Database CRUD API                   ║
║         EWB Edu Tech Pvt. Ltd. | Internship Project             ║
╚══════════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import students, ai_assistant, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    init_db()
    yield


app = FastAPI(
    title="📚 EduTrack — Student Database API",
    description="""
## 🎓 EduTrack Student Management System

A production-ready **FastAPI + SQLite** backend for managing student records.

### Features
- ✅ Full **CRUD** operations on student records
- 🔍 **Filter & search** students by name, course, or date range
- 🤖 **AI Assistant** — ask natural-language questions about the student data (Ollama integration)
- 🛡️ Input validation, error handling & meaningful HTTP status codes
- 📄 Auto-generated interactive docs (you're here!)

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

---
*Built for EWB Edu Tech Pvt. Ltd. Internship Program*
    """,
    version="1.0.0",
    contact={
        "name": "EWB Edu Tech Pvt. Ltd.",
        "url": "https://github.com/",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)

# Allow all origins for development / demo purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(students.router, prefix="/students", tags=["👤 Students"])
app.include_router(ai_assistant.router, prefix="/ai", tags=["🤖 AI Assistant"])
app.include_router(stats.router, prefix="/stats", tags=["📊 Stats & Balance"])


# ── Root landing page ──────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>EduTrack API</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet"/>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;}
            body{font-family:'Inter',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);
                 min-height:100vh;display:flex;align-items:center;justify-content:center;color:#fff;}
            .card{background:rgba(255,255,255,0.07);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.15);
                  border-radius:24px;padding:60px 50px;max-width:680px;width:90%;text-align:center;
                  box-shadow:0 30px 80px rgba(0,0,0,0.5);}
            .badge{display:inline-block;background:linear-gradient(90deg,#667eea,#764ba2);
                   padding:6px 18px;border-radius:50px;font-size:12px;font-weight:600;
                   letter-spacing:1px;text-transform:uppercase;margin-bottom:28px;}
            h1{font-size:3rem;font-weight:900;letter-spacing:-1px;
               background:linear-gradient(90deg,#a78bfa,#60a5fa,#34d399);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;}
            p.sub{font-size:1.05rem;color:rgba(255,255,255,0.6);line-height:1.7;margin-bottom:38px;}
            .links{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;}
            a.btn{display:inline-flex;align-items:center;gap:8px;padding:14px 28px;
                  border-radius:12px;font-weight:600;font-size:0.95rem;text-decoration:none;
                  transition:transform .2s,box-shadow .2s;}
            .btn-primary{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;
                         box-shadow:0 8px 25px rgba(102,126,234,0.4);}
            .btn-secondary{background:rgba(255,255,255,0.1);color:#fff;
                           border:1px solid rgba(255,255,255,0.2);}
            .btn:hover{transform:translateY(-3px);box-shadow:0 12px 35px rgba(102,126,234,0.5);}
            .chips{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:36px;}
            .chip{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);
                  border-radius:8px;padding:8px 14px;font-size:0.8rem;color:rgba(255,255,255,0.7);}
            .dot{width:8px;height:8px;border-radius:50%;background:#34d399;
                 display:inline-block;margin-right:6px;animation:pulse 2s infinite;}
            @keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.4;}}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">🎓 EWB Edu Tech Internship</div>
            <h1>EduTrack API</h1>
            <p class="sub">
                A blazing-fast <strong>Student Database Management System</strong> built with
                <strong>FastAPI + SQLite</strong>. Manage student records with full CRUD
                operations and an optional AI assistant powered by Ollama.
            </p>
            <div class="links">
                <a class="btn btn-primary" href="/docs">📄 Swagger UI</a>
                <a class="btn btn-secondary" href="/redoc">📘 ReDoc</a>
                <a class="btn btn-secondary" href="/stats/dashboard">📊 Stats Dashboard</a>
                <a class="btn btn-secondary" href="/students">🔗 Students API</a>
            </div>
            <div class="chips">
                <span class="chip"><span class="dot"></span>Server Online</span>
                <span class="chip">🐍 Python + FastAPI</span>
                <span class="chip">🗄️ SQLite</span>
                <span class="chip">🤖 Ollama AI</span>
                <span class="chip">📊 Stats & Balance</span>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
