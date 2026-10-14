"""
Stats / Balance router.

Routes
------
GET /stats/summary        — JSON summary (totals, breakdowns)
GET /stats/dashboard      — HTML visual dashboard (charts + cards)
"""

from collections import Counter
from datetime import date, datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student

router = APIRouter()


# ── helpers ────────────────────────────────────────────────────────────────────

def _calc_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _compute_stats(db: Session) -> Dict[str, Any]:
    students: List[Student] = db.query(Student).all()
    total = len(students)

    if total == 0:
        return {
            "total_students": 0,
            "courses": {},
            "top_courses": [],
            "age_distribution": {},
            "enrollment_by_year": {},
            "avg_age": None,
            "newest_student": None,
            "oldest_student": None,
        }

    # Course breakdown
    course_counter: Counter = Counter()
    for s in students:
        course_counter[s.course or "Unspecified"] += 1

    # Age distribution
    ages = []
    age_groups: Counter = Counter()
    for s in students:
        try:
            age = _calc_age(s.date_of_birth)
            ages.append(age)
            if age < 18:
                age_groups["< 18"] += 1
            elif age <= 21:
                age_groups["18 – 21"] += 1
            elif age <= 25:
                age_groups["22 – 25"] += 1
            elif age <= 30:
                age_groups["26 – 30"] += 1
            else:
                age_groups["> 30"] += 1
        except Exception:
            pass

    # Enrollment by year
    enroll_years: Counter = Counter()
    for s in students:
        if s.enrollment_date:
            enroll_years[str(s.enrollment_date.year)] += 1

    top_courses = [
        {"course": c, "count": n} for c, n in course_counter.most_common(5)
    ]

    return {
        "total_students": total,
        "courses": dict(course_counter),
        "top_courses": top_courses,
        "age_distribution": dict(sorted(age_groups.items())),
        "enrollment_by_year": dict(sorted(enroll_years.items())),
        "avg_age": round(sum(ages) / len(ages), 1) if ages else None,
        "newest_student": max(
            (s.created_at for s in students if s.created_at), default=None
        ),
        "oldest_student": min(
            (s.created_at for s in students if s.created_at), default=None
        ),
    }


# ── JSON summary ───────────────────────────────────────────────────────────────

@router.get(
    "/summary",
    summary="Student statistics summary (JSON)",
    description=(
        "Returns a JSON object with key balance metrics: total students, "
        "course distribution, age groups, and enrollment trends."
    ),
)
def stats_summary(db: Session = Depends(get_db)):
    return _compute_stats(db)


# ── HTML Dashboard ─────────────────────────────────────────────────────────────

@router.get(
    "/dashboard",
    response_class=HTMLResponse,
    include_in_schema=False,
    summary="Visual statistics dashboard",
)
def stats_dashboard(db: Session = Depends(get_db)):
    data = _compute_stats(db)
    total = data["total_students"]
    avg_age = data["avg_age"] or "N/A"
    top = data["top_courses"]
    age_dist = data["age_distribution"]
    enroll_by_year = data["enrollment_by_year"]
    course_dist = data["courses"]
    generated = datetime.now().strftime("%d %b %Y, %H:%M")

    # ── Donut slices for course distribution ──
    colors = ["#a78bfa", "#60a5fa", "#34d399", "#fb923c", "#f472b6",
              "#facc15", "#38bdf8", "#4ade80", "#f87171", "#c084fc"]

    def donut_slices(data_dict: dict, size: int = 120) -> str:
        total = sum(data_dict.values()) or 1
        slices = []
        offset = 0.0
        r = 40
        circ = 2 * 3.14159 * r
        for i, (label, val) in enumerate(data_dict.items()):
            pct = val / total
            dash = pct * circ
            color = colors[i % len(colors)]
            slices.append(
                f'<circle cx="{size//2}" cy="{size//2}" r="{r}" fill="none"'
                f' stroke="{color}" stroke-width="18"'
                f' stroke-dasharray="{dash:.2f} {circ:.2f}"'
                f' stroke-dashoffset="-{offset:.2f}"'
                f' transform="rotate(-90 {size//2} {size//2})"/>'
            )
            offset += dash
        return "".join(slices)

    donut_course = donut_slices(course_dist) if course_dist else ""
    donut_age = donut_slices(age_dist) if age_dist else ""

    # ── Bar chart for enrollment by year ──
    def bar_chart(data_dict: dict) -> str:
        if not data_dict:
            return "<p style='color:rgba(255,255,255,0.4);text-align:center;padding:20px;'>No enrollment data</p>"
        max_val = max(data_dict.values()) or 1
        bars = []
        for i, (yr, cnt) in enumerate(data_dict.items()):
            h = int((cnt / max_val) * 80)
            col = colors[i % len(colors)]
            bars.append(f"""
              <div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;min-width:50px;">
                <span style="font-size:0.75rem;color:rgba(255,255,255,0.7);">{cnt}</span>
                <div style="width:36px;height:{h}px;background:{col};border-radius:6px 6px 0 0;
                     box-shadow:0 0 12px {col}55;transition:height .3s;"></div>
                <span style="font-size:0.7rem;color:rgba(255,255,255,0.5);">{yr}</span>
              </div>""")
        return (
            '<div style="display:flex;align-items:flex-end;gap:10px;height:120px;'
            'padding:0 10px;justify-content:center;">' + "".join(bars) + "</div>"
        )

    def legend_items(data_dict: dict) -> str:
        items = []
        for i, (label, val) in enumerate(data_dict.items()):
            col = colors[i % len(colors)]
            items.append(
                f'<div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:rgba(255,255,255,0.75);">'
                f'<span style="width:12px;height:12px;border-radius:3px;background:{col};flex-shrink:0;"></span>'
                f'<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{label}</span>'
                f'<strong style="color:#fff;">{val}</strong></div>'
            )
        return "".join(items)

    top_courses_rows = "".join(
        f"""<tr>
          <td style="padding:10px 14px;color:rgba(255,255,255,0.9);">{i+1}. {t['course']}</td>
          <td style="padding:10px 14px;text-align:right;">
            <span style="background:linear-gradient(90deg,#667eea,#764ba2);padding:3px 12px;
            border-radius:20px;font-size:0.82rem;font-weight:600;">{t['count']}</span>
          </td>
          <td style="padding:10px 14px;">
            <div style="background:rgba(255,255,255,0.08);border-radius:20px;height:8px;overflow:hidden;">
              <div style="width:{int(t['count']/max(tt['count'] for tt in top) * 100) if top else 0}%;
              height:100%;background:linear-gradient(90deg,#a78bfa,#60a5fa);border-radius:20px;"></div>
            </div>
          </td>
        </tr>"""
        for i, t in enumerate(top)
    ) if top else "<tr><td colspan='3' style='padding:20px;text-align:center;color:rgba(255,255,255,0.4);'>No course data</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>EduTrack Stats Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{
      font-family: 'Inter', sans-serif;
      background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
      min-height: 100vh;
      color: #fff;
      padding: 40px 20px;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    /* Header */
    .header {{ text-align:center; margin-bottom:48px; }}
    .badge {{
      display:inline-block;
      background:linear-gradient(90deg,#667eea,#764ba2);
      padding:6px 20px; border-radius:50px;
      font-size:11px; font-weight:700; letter-spacing:2px;
      text-transform:uppercase; margin-bottom:18px;
    }}
    h1 {{
      font-size:2.8rem; font-weight:900; letter-spacing:-1px;
      background:linear-gradient(90deg,#a78bfa,#60a5fa,#34d399);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
      margin-bottom:10px;
    }}
    .sub {{ color:rgba(255,255,255,0.5); font-size:0.95rem; }}
    /* Cards grid */
    .kpi-grid {{
      display:grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap:20px; margin-bottom:32px;
    }}
    .kpi {{
      background:rgba(255,255,255,0.06);
      border:1px solid rgba(255,255,255,0.12);
      border-radius:18px; padding:28px 24px;
      display:flex; flex-direction:column; gap:8px;
      backdrop-filter:blur(10px);
      transition:transform .2s, box-shadow .2s;
    }}
    .kpi:hover {{ transform:translateY(-4px); box-shadow:0 20px 40px rgba(0,0,0,0.3); }}
    .kpi-icon {{ font-size:1.6rem; }}
    .kpi-value {{ font-size:2.4rem; font-weight:900; }}
    .kpi-label {{ font-size:0.78rem; color:rgba(255,255,255,0.5); text-transform:uppercase; letter-spacing:1px; }}
    /* Charts grid */
    .charts-grid {{
      display:grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap:24px; margin-bottom:32px;
    }}
    .card {{
      background:rgba(255,255,255,0.05);
      border:1px solid rgba(255,255,255,0.1);
      border-radius:20px;
      padding:28px;
      backdrop-filter:blur(10px);
    }}
    .card-title {{
      font-size:0.85rem; font-weight:700; letter-spacing:1.5px;
      text-transform:uppercase; color:rgba(255,255,255,0.5);
      margin-bottom:22px; display:flex; align-items:center; gap:8px;
    }}
    .donut-wrap {{ display:flex; align-items:center; gap:24px; flex-wrap:wrap; }}
    .legend {{ display:flex; flex-direction:column; gap:8px; flex:1; min-width:120px; }}
    table {{ width:100%; border-collapse:collapse; }}
    tr:nth-child(even) {{ background:rgba(255,255,255,0.03); }}
    tr:hover {{ background:rgba(255,255,255,0.06); }}
    .nav-back {{
      display:inline-flex; align-items:center; gap:8px;
      background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15);
      border-radius:10px; padding:10px 18px;
      color:#fff; text-decoration:none; font-weight:600; font-size:0.88rem;
      margin-bottom:32px; transition:background .2s;
    }}
    .nav-back:hover {{ background:rgba(255,255,255,0.14); }}
    .footer {{
      text-align:center; margin-top:48px;
      color:rgba(255,255,255,0.25); font-size:0.78rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <a class="nav-back" href="/">← Back to Home</a>

    <!-- Header -->
    <div class="header">
      <div class="badge">📊 Live Analytics</div>
      <h1>EduTrack Stats Dashboard</h1>
      <p class="sub">Real-time student data balance &amp; distribution · Generated {generated}</p>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi">
        <span class="kpi-icon">🎓</span>
        <span class="kpi-value" style="background:linear-gradient(90deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{total}</span>
        <span class="kpi-label">Total Students</span>
      </div>
      <div class="kpi">
        <span class="kpi-icon">📚</span>
        <span class="kpi-value" style="background:linear-gradient(90deg,#34d399,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{len(course_dist)}</span>
        <span class="kpi-label">Unique Courses</span>
      </div>
      <div class="kpi">
        <span class="kpi-icon">🎂</span>
        <span class="kpi-value" style="background:linear-gradient(90deg,#fb923c,#f472b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{avg_age}</span>
        <span class="kpi-label">Average Age</span>
      </div>
      <div class="kpi">
        <span class="kpi-icon">📅</span>
        <span class="kpi-value" style="background:linear-gradient(90deg,#facc15,#fb923c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{len(enroll_by_year)}</span>
        <span class="kpi-label">Enrollment Years</span>
      </div>
    </div>

    <!-- Charts -->
    <div class="charts-grid">

      <!-- Course Donut -->
      <div class="card">
        <div class="card-title">📈 Course Distribution</div>
        {'<div class="donut-wrap"><svg width="120" height="120" viewBox="0 0 120 120">' + donut_course + '</svg><div class="legend">' + legend_items(course_dist) + '</div></div>'
          if course_dist else '<p style="color:rgba(255,255,255,0.4);text-align:center;padding:30px;">No data yet</p>'}
      </div>

      <!-- Age Donut -->
      <div class="card">
        <div class="card-title">🎂 Age Group Balance</div>
        {'<div class="donut-wrap"><svg width="120" height="120" viewBox="0 0 120 120">' + donut_age + '</svg><div class="legend">' + legend_items(age_dist) + '</div></div>'
          if age_dist else '<p style="color:rgba(255,255,255,0.4);text-align:center;padding:30px;">No data yet</p>'}
      </div>

      <!-- Enrollment Bar Chart -->
      <div class="card">
        <div class="card-title">📅 Enrollments by Year</div>
        {bar_chart(enroll_by_year)}
      </div>

    </div>

    <!-- Top Courses Table -->
    <div class="card">
      <div class="card-title">🏆 Top Courses by Enrollment</div>
      <table>
        <tbody>
          {top_courses_rows}
        </tbody>
      </table>
    </div>

    <div class="footer">EduTrack · EWB Edu Tech Pvt. Ltd. · Internship Project · Generated {generated}</div>
  </div>
</body>
</html>"""
    return HTMLResponse(content=html)
