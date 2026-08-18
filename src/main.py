#!/usr/bin/env python3
"""
=============================================================================
IIT Patna M.Tech (AI & Data Science) - Main Course & Curriculum Manager
=============================================================================
Reads:
  - Classes/timetable_web.html (Official Timetable Grid)
  - courses/all_courses.json   (Master 24-Course Database)
  - Curriculum configuration (Core & Elective selections for all 4 Semesters)

Updates:
  - d:/IITP/index.html & d:/IITP/output/index.html (Single-Semester Dashboard)
=============================================================================
"""

import os
import sys
import re
import json
import base64

# Setup paths
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
LOGO_IMAGE_PATH = os.path.join(ROOT_DIR, 'image', 'logo.png')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import sync_timetable_and_courses as synchronizer

# Default Selected Curriculum
MY_CURRICULUM_SELECTION = {
    "semester_1": {
        "core_courses": [
            "ECS 5101",  # Design and Analysis of Algorithms
            "ECS 5102",  # Foundations of Computer Systems
            "EMC 5103",  # Probability and Statistics
            "EHS 5104",  # Technical Writing and Soft Skill
        ],
        "elective_1": "EAI 6103",  # Advance Machine Learning
    },
    "semester_2": {
        "core_courses": [
            "ECS 5201",  # Artificial Intelligence
            "EMC 5202",  # Numerical Linear Algebra and Optimization Techniques
            "IKS",       # Indian Knowledge System
        ],
        "electives": [
            "EAI 6202",  # Physics of Neural Network
            "EAI 6204",  # Federated Learning
        ],
    },
    "semester_3": {
        "major_project": "Project I",  # Major Project I (17 Credits)
        "electives": [
            "EAI 6301",  # Artificial Internet of Things
            "EAI 6302",  # Natural Language Processing
        ],
    },
    "semester_4": {
        "major_project": "Project II",  # Major Project II (20 Credits)
        "electives": [
            "EAI 6401",  # Reinforcement Learning
            "EAI 6402",  # Meta Learning
        ],
    }
}

SEMESTER_META = {
    1: {"name": "Semester I", "credits": 19, "period": "Instruction: 16 August – 30 November 2026", "badge": "Active (19 Credits)"},
    2: {"name": "Semester II", "credits": 16, "period": "Spring Semester • Scheduled Start: 23 January 2027", "badge": "Spring 2027 (16 Credits)"},
    3: {"name": "Semester III", "credits": 23, "period": "Autumn Semester • Commencing July / August 2027", "badge": "Autumn 2027 (23 Credits)"},
    4: {"name": "Semester IV", "credits": 26, "period": "Final Spring Semester • Commencing January 2028", "badge": "Spring 2028 (26 Credits)"}
}


def resolve_course_data(query_str, catalog):
    """Finds and returns the complete course object from the catalog."""
    query_clean = str(query_str).lower().strip().replace('/', '').replace('-', '').replace(' ', '')

    for course in catalog:
        c_code = course.get('subject_code', '').lower().replace('/', '').replace('-', '').replace(' ', '')
        c_name = course.get('subject_name', '').lower()

        if query_clean == c_code or query_clean in c_code or query_clean in c_name.replace(' ', ''):
            return course

    return {
        "subject_code": str(query_str),
        "subject_name": str(query_str),
        "credits": "3 Credits",
        "description": "Course details as configured.",
        "learning_objectives": [],
        "outline": [],
        "books": []
    }


def generate_single_chip_html(course_obj, tag_label="CORE", tag_class="course-tag-core", faculty_text="👤 IIT Patna Faculty", border_style=""):
    """Generates HTML markup for a single interactive course chip."""
    code = course_obj.get('subject_code', 'N/A')
    name = course_obj.get('subject_name', 'Untitled')
    credits_str = course_obj.get('credits', '').replace('Credits', 'Cr').replace('(L-T-P-C:', '•').replace(')', '').strip()

    style_attr = f' style="{border_style}"' if border_style else ''

    return f"""          <div class="subject-chip" onclick="openCourseModal('{code}')" title="Click to view Learning Objectives, Syllabus & Reference Books"{style_attr}>
            <div class="chip-top">
              <span class="course-tag {tag_class}">{tag_label} • {code}</span>
              <span style="font-size:0.75rem; font-family:var(--font-mono); color:var(--core-color);">{credits_str}</span>
            </div>
            <div class="chip-title">{name}</div>
            <div class="chip-faculty">{faculty_text}</div>
            <div class="clickable-cue">📖 View Objectives & Books →</div>
          </div>"""


def generate_semester_chips_html(sem_num, config, catalog, timetable_data):
    """Generates the complete <div class="subject-chips-grid">...</div> for a given semester."""
    chips = []

    if sem_num == 1:
        sem1_faculty = {
            "ECS 5101": "👤 Dr. Rahul Mishra • Sat & Sun",
            "ECS 5102": "👤 Mr. Sundar Doraiswami • Sat & Sun",
            "EMC 5103": "👤 Dr. Anuj Singh • Mon, Wed & Thu",
            "EHS 5104": "👤 Dr. Sweta Sinha • Tue & Wed",
        }
        for code in ["ECS 5101", "ECS 5102", "EMC 5103", "EHS 5104"]:
            c_data = resolve_course_data(code, catalog)
            fac = sem1_faculty.get(code, "👤 IIT Patna Faculty")
            chips.append(generate_single_chip_html(c_data, tag_label="CORE", tag_class="course-tag-core", faculty_text=fac))

        e1_input = config.get("semester_1", {}).get("elective_1", "EAI 6103")
        e1_data = resolve_course_data(e1_input, catalog)
        e1_code = e1_data.get('subject_code', 'EAI 6103')

        tt_match = next((v for k, v in timetable_data.items() if e1_code.replace(' ', '') in k.replace(' ', '')), None)
        fac_e1 = f"👤 {tt_match['faculty']}" if tt_match else "👤 Selected Elective from Pool (DE-1)"

        chips.append(generate_single_chip_html(
            e1_data,
            tag_label="ELECTIVE I",
            tag_class="course-tag-elec",
            faculty_text=fac_e1,
            border_style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.05);"
        ))

    elif sem_num == 2:
        for code in ["ECS 5201", "EMC 5202", "IKS"]:
            c_data = resolve_course_data(code, catalog)
            chips.append(generate_single_chip_html(c_data, tag_label="CORE", tag_class="course-tag-core", faculty_text="👤 IIT Patna Faculty • Core Subject"))

        e_list = config.get("semester_2", {}).get("electives", ["EAI 6202", "EAI 6204"])
        for idx, e_input in enumerate(e_list, 2):
            e_data = resolve_course_data(e_input, catalog)
            chips.append(generate_single_chip_html(
                e_data,
                tag_label=f"ELECTIVE {['II', 'III'][idx-2] if idx <= 3 else idx}",
                tag_class="course-tag-elec",
                faculty_text=f"👤 Selected Elective from Pool (DE-{idx})",
                border_style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.05);"
            ))

    elif sem_num == 3:
        proj1 = resolve_course_data("Project I", catalog)
        chips.append(generate_single_chip_html(
            proj1,
            tag_label="PROJECT • MAJOR",
            tag_class="course-tag-proj",
            faculty_text="👤 Research / Industry Thesis Part 1",
            border_style="border-color: rgba(192, 132, 252, 0.4); background: rgba(192, 132, 252, 0.05);"
        ))

        e_list = config.get("semester_3", {}).get("electives", ["EAI 6301", "EAI 6302"])
        for idx, e_input in enumerate(e_list, 4):
            e_data = resolve_course_data(e_input, catalog)
            chips.append(generate_single_chip_html(
                e_data,
                tag_label=f"ELECTIVE {['IV', 'V'][idx-4] if idx <= 5 else idx}",
                tag_class="course-tag-elec",
                faculty_text=f"👤 Selected Elective from Pool (DE-{idx})",
                border_style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.05);"
            ))

    elif sem_num == 4:
        proj2 = resolve_course_data("Project II", catalog)
        chips.append(generate_single_chip_html(
            proj2,
            tag_label="PROJECT • MAJOR",
            tag_class="course-tag-proj",
            faculty_text="👤 Final M.Tech Capstone Project & Dissertation",
            border_style="border-color: rgba(192, 132, 252, 0.4); background: rgba(192, 132, 252, 0.05);"
        ))

        e_list = config.get("semester_4", {}).get("electives", ["EAI 6401", "EAI 6402"])
        for idx, e_input in enumerate(e_list, 6):
            e_data = resolve_course_data(e_input, catalog)
            chips.append(generate_single_chip_html(
                e_data,
                tag_label=f"ELECTIVE {['VI', 'VII'][idx-6] if idx <= 7 else idx}",
                tag_class="course-tag-elec",
                faculty_text=f"👤 Selected Elective from Pool (DE-{idx})",
                border_style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.05);"
            ))

    chips_inner = "\n\n".join(chips)
    return f"""<div class="subject-chips-grid">\n{chips_inner}\n        </div>"""


def render_full_dashboard_html(active_semester, config, catalog, timetable_data, user_sem1_courses, holidays_map=None):
    """
    Renders the complete index.html dashboard tailored for the chosen active_semester,
    dynamically embedding synchronized holidays and timetable slots.
    """
    if holidays_map is None:
        holidays_map = {}
    holidays_json = json.dumps(holidays_map)

    meta = SEMESTER_META.get(active_semester, SEMESTER_META[1])
    sem_name = meta["name"]
    credits_num = meta["credits"]
    period_str = meta["period"]
    badge_str = meta["badge"]

    chips_grid_html = generate_semester_chips_html(active_semester, config, catalog, timetable_data)

    if active_semester == 1:
        # Semester 1 Full Detail Content (Attendance stats, today's schedule, tracker, timetable, milestones, analytics)
        semester_body_html = f"""
      <!-- Selected Subjects Overview Banner -->
      <div class="sem-overview-card">
        <div class="sem-overview-header">
          <h2>
            <span>📚</span>
            <span>{sem_name} Selected Curriculum ({credits_num} Credits)</span>
          </h2>
          <span style="font-size:0.8rem; color:var(--text-secondary);">{period_str}</span>
        </div>
        {chips_grid_html}
      </div>

      <!-- Symmetrical 5-Card Statistics Dashboard for Semester 1 -->
      <div class="stats-grid">
        <!-- Card 1: Attendance Health Metric -->
        <div class="stat-card hero-attendance-card">
          <div class="stat-header">
            <span class="stat-title">Attendance Health</span>
            <div class="stat-icon-wrap" style="color: var(--accent-emerald); background: rgba(5, 150, 105, 0.12);">📊</div>
          </div>
          <div class="stat-value" id="heroGaugePct" style="color: var(--accent-emerald);">100%</div>
          <div class="stat-meta" id="heroAttendanceStatus" style="font-weight: 600; color: var(--accent-emerald);">
            <span class="status-indicator status-good"></span> ≥ 75% Compliant
          </div>
        </div>

        <!-- Card 2: Classes Attended -->
        <div class="stat-card">
          <div class="stat-header">
            <span class="stat-title">Classes Attended</span>
            <div class="stat-icon-wrap" style="color: var(--accent-emerald); background: rgba(5, 150, 105, 0.12);">✓</div>
          </div>
          <div class="stat-value" id="statAttendedCount" style="color: var(--accent-emerald);">0</div>
          <div class="stat-meta" id="statAttendedBreakdown">Live: 0 | Recorded: 0</div>
        </div>

        <!-- Card 3: Classes Cancelled -->
        <div class="stat-card">
          <div class="stat-header">
            <span class="stat-title">Classes Cancelled</span>
            <div class="stat-icon-wrap" style="color: #ea580c; background: rgba(234, 88, 12, 0.12);">🚫</div>
          </div>
          <div class="stat-value" id="statCancelledCount" style="color: #ea580c;">0</div>
          <div class="stat-meta" id="statCancelledMeta">Faculty Cancellations</div>
        </div>

        <!-- Card 4: Total Conducted -->
        <div class="stat-card">
          <div class="stat-header">
            <span class="stat-title">Total Conducted</span>
            <div class="stat-icon-wrap" style="color: var(--accent-blue); background: rgba(2, 132, 199, 0.12);">📅</div>
          </div>
          <div class="stat-value" id="statTotalPastClasses">0</div>
          <div class="stat-meta" id="statTotalSemesterClasses">of 176 semester sessions</div>
        </div>

        <!-- Card 5: Safe Bunk Margin -->
        <div class="stat-card">
          <div class="stat-header">
            <span class="stat-title">Safe Bunk Margin</span>
            <div class="stat-icon-wrap" style="color: var(--accent-purple); background: rgba(147, 51, 234, 0.12);">🛡️</div>
          </div>
          <div class="stat-value" id="statBunksAllowed" style="color: var(--accent-purple);">44</div>
          <div class="stat-meta" id="statBunksMeta">Safe misses for sem 1</div>
        </div>
      </div>

      <!-- Today's Live Schedule Widget -->
      <div class="today-banner">
        <div class="today-header">
          <h3>
            <span>📅</span>
            <span id="todayHeaderDate">Today's Class Schedule</span>
          </h3>
          <div style="display:flex; gap:0.5rem; align-items:center;">
            <span class="badge-pill" id="todayClassesCountBadge">0 Classes Scheduled</span>
            <button class="btn btn-sm" onclick="markAllTodayAttended('live')" style="color: var(--accent-emerald);">✓ Mark All Live</button>
            <button class="btn btn-sm" onclick="markAllTodayAttended('rec')" style="color: var(--accent-blue);">🎥 Mark All Rec</button>
          </div>
        </div>
        <div class="today-list" id="todayScheduleList">
          <!-- Dynamic classes today injected by JavaScript -->
        </div>
      </div>

      <!-- Sub-tabs Navigation for Semester 1 -->
      <nav class="sub-tabs-nav">
        <button class="sub-tab-btn active" onclick="switchSubTab('trackerSubPane', this)">
          <span>📅</span>
          <span>Date-by-Date Schedule &amp; Attendance Tracker</span>
        </button>
        <button class="sub-tab-btn" onclick="switchSubTab('milestonesSubPane', this)">
          <span>🎯</span>
          <span>Academic Milestones &amp; Exam Weightage</span>
        </button>
        <button class="sub-tab-btn" onclick="switchSubTab('analyticsSubPane', this)">
          <span>📊</span>
          <span>Enrolled Subject Analytics &amp; Syllabi</span>
        </button>
      </nav>

      <!-- SUB-PANE 1: Date-by-Date Schedule Tracker -->
      <div class="sub-pane active" id="trackerSubPane">
        <div class="controls-bar">
          <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input class="search-input" id="classSearchInput" oninput="renderTrackerTable()" placeholder="Search by subject, code, faculty, or YYYY-MM-DD..." type="text"/>
          </div>
          <div class="filters-group">
            <button class="btn btn-sm" id="collapseAllBtn" onclick="toggleCollapseAll()" style="font-weight:700; color:var(--primary); background:var(--bg-secondary); border:1px solid var(--border-color); padding:0.6rem 0.9rem; border-radius:var(--radius-md); cursor:pointer;">
              📁 Expand All Weeks
            </button>
            <select class="select-dropdown" id="filterWeek" onchange="renderTrackerTable()">
              <option value="all">📅 All Weeks (Week 1 – 16)</option>
            </select>
            <select class="select-dropdown" id="filterCourse" onchange="renderTrackerTable()">
              <option value="all">📚 All 5 Courses</option>
            </select>
            <select class="select-dropdown" id="filterStatus" onchange="renderTrackerTable()">
              <option value="all">⚡ All Statuses</option>
              <option value="live">✅ Attended Live</option>
              <option value="rec">🎥 Attended Recorded</option>
              <option value="cancelled">🚫 Cancelled (Faculty)</option>
              <option value="unmarked">⚪ Unmarked Sessions</option>
            </select>
          </div>
        </div>

        <div class="schedule-table-card">
          <div class="table-responsive">
            <table class="custom-table" id="trackerTable">
              <thead>
                <tr>
                  <th style="width: 16%;">Date &amp; Day</th>
                  <th style="width: 15%;">Time Slot</th>
                  <th style="width: 32%;">Course &amp; Faculty</th>
                  <th style="width: 22%;">Attendance Status</th>
                  <th style="width: 15%;">Personal Notes</th>
                </tr>
              </thead>
              <tbody id="trackerTableBody">
                <!-- Injected via JavaScript -->
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- SUB-PANE 2: Academic Milestones -->
      <div class="sub-pane" id="milestonesSubPane">
        <!-- Official Evaluation & Grading Policy from 1sem_timetable.pdf -->
        <div class="weightage-bar-card" style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 1.5rem; margin-bottom: 1.5rem;">
          <h3 style="font-size: 1.1rem; font-weight: 800; margin-bottom: 0.5rem; color: #1e1b4b;">Official Evaluation &amp; Grading Weightage Policy</h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.25rem;">
            As prescribed in the official academic calendar (Executive/Hybrid PG Programs). All quizzes and exams are conducted via <strong>Proctored Online Mode</strong>. Minimum <strong>75% attendance</strong> is mandatory.
          </p>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
            <div style="background: var(--bg-secondary); padding: 1.1rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); border-left: 5px solid var(--primary);">
              <div style="font-size: 1.6rem; font-weight: 800; color: var(--primary);">30%</div>
              <div style="font-weight: 700; color: #000000; margin-top: 0.2rem;">Assignments (4 Tasks)</div>
              <span style="font-size: 0.75rem; color: var(--text-secondary);">Sep 11–15, Sep 25–Oct 01, Oct 25–29, Nov 08–12</span>
            </div>
            <div style="background: var(--bg-secondary); padding: 1.1rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); border-left: 5px solid var(--accent-blue);">
              <div style="font-size: 1.6rem; font-weight: 800; color: var(--accent-blue);">20%</div>
              <div style="font-weight: 700; color: #000000; margin-top: 0.2rem;">Quizzes (2 Proctored)</div>
              <span style="font-size: 0.75rem; color: var(--text-secondary);">Quiz 1: Oct 11–15 | Quiz 2: Nov 22–26</span>
            </div>
            <div style="background: rgba(5, 150, 105, 0.08); padding: 1.1rem; border-radius: var(--radius-md); border: 1px solid rgba(5, 150, 105, 0.3); border-left: 5px solid #059669;">
              <div style="font-size: 1.6rem; font-weight: 800; color: #059669;">50%</div>
              <div style="font-weight: 700; color: #065f46; margin-top: 0.2rem;">End Semester Exam (ESE)</div>
              <span style="font-size: 0.75rem; color: #047857; font-weight: 600;">Dec 01 – Dec 30, 2026 (Weekends: Sat &amp; Sun)</span>
            </div>
          </div>
        </div>

        <!-- Post-Instruction Exam & Result Timeline in Green Theme -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 1.5rem; margin-bottom: 1.5rem;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem; flex-wrap:wrap; gap:0.5rem;">
            <h3 style="font-size: 1.15rem; font-weight: 800; margin: 0; color: #065f46; display:flex; align-items:center; gap:0.5rem;">
              <span>🎓</span>
              <span>Post-Instruction Examination, Evaluation &amp; Result Timeline</span>
            </h3>
            <span style="font-size:0.75rem; font-weight:700; color:#059669; background:rgba(5,150,105,0.12); padding:0.3rem 0.75rem; border-radius:6px; border:1px solid rgba(5,150,105,0.25);">
              Official Calendar (Dec 2026 – Jan 2027)
            </span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
            <!-- Milestone 1 -->
            <div style="background: rgba(5, 150, 105, 0.05); border: 1px solid rgba(5, 150, 105, 0.25); border-left: 5px solid #059669; border-radius: var(--radius-md); padding: 1.1rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.72rem; font-weight:800; color:#ffffff; background:#059669; padding:0.2rem 0.55rem; border-radius:4px;">50% ESE</span>
                <span style="font-size:0.75rem; font-weight:700; color:#059669;">Dec 01 – Dec 30, 2026</span>
              </div>
              <h4 style="font-size:1rem; font-weight:800; color:#065f46; margin:0.5rem 0 0.25rem 0;">End Semester Exam (ESE)</h4>
              <p style="font-size:0.82rem; color:#047857; margin:0; line-height:1.45;">Proctored Online Mode. Conducted exclusively on weekends (Saturdays &amp; Sundays).</p>
            </div>

            <!-- Milestone 2 -->
            <div style="background: rgba(5, 150, 105, 0.05); border: 1px solid rgba(5, 150, 105, 0.25); border-left: 5px solid #059669; border-radius: var(--radius-md); padding: 1.1rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.72rem; font-weight:800; color:#065f46; background:rgba(5,150,105,0.15); padding:0.2rem 0.55rem; border-radius:4px;">GRADING</span>
                <span style="font-size:0.75rem; font-weight:700; color:#059669;">10 January, 2027</span>
              </div>
              <h4 style="font-size:1rem; font-weight:800; color:#065f46; margin:0.5rem 0 0.25rem 0;">Project Grade Submission</h4>
              <p style="font-size:0.82rem; color:#047857; margin:0; line-height:1.45;">Last date for department faculty submission of project &amp; lab evaluation grades.</p>
            </div>

            <!-- Milestone 3 -->
            <div style="background: rgba(5, 150, 105, 0.05); border: 1px solid rgba(5, 150, 105, 0.25); border-left: 5px solid #059669; border-radius: var(--radius-md); padding: 1.1rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.72rem; font-weight:800; color:#ffffff; background:#059669; padding:0.2rem 0.55rem; border-radius:4px;">RESULTS</span>
                <span style="font-size:0.75rem; font-weight:700; color:#059669;">20 January, 2027</span>
              </div>
              <h4 style="font-size:1rem; font-weight:800; color:#065f46; margin:0.5rem 0 0.25rem 0;">Declaration of Results</h4>
              <p style="font-size:0.82rem; color:#047857; margin:0; line-height:1.45;">Provisional publication of Semester 1 course scores and grades on academic portal.</p>
            </div>

            <!-- Milestone 4 -->
            <div style="background: rgba(5, 150, 105, 0.05); border: 1px solid rgba(5, 150, 105, 0.25); border-left: 5px solid #059669; border-radius: var(--radius-md); padding: 1.1rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.72rem; font-weight:800; color:#065f46; background:rgba(5,150,105,0.15); padding:0.2rem 0.55rem; border-radius:4px;">REVISION</span>
                <span style="font-size:0.75rem; font-weight:700; color:#059669;">21 January, 2027</span>
              </div>
              <h4 style="font-size:1rem; font-weight:800; color:#065f46; margin:0.5rem 0 0.25rem 0;">Grade Revision Claims</h4>
              <p style="font-size:0.82rem; color:#047857; margin:0; line-height:1.45;">Last date for student submission of grade revision or re-evaluation requests.</p>
            </div>

            <!-- Milestone 5 -->
            <div style="background: rgba(5, 150, 105, 0.05); border: 1px solid rgba(5, 150, 105, 0.25); border-left: 5px solid #059669; border-radius: var(--radius-md); padding: 1.1rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.72rem; font-weight:800; color:#ffffff; background:#059669; padding:0.2rem 0.55rem; border-radius:4px;">FINAL GRADES</span>
                <span style="font-size:0.75rem; font-weight:700; color:#059669;">22 January, 2027</span>
              </div>
              <h4 style="font-size:1rem; font-weight:800; color:#065f46; margin:0.5rem 0 0.25rem 0;">Final Result Declaration</h4>
              <p style="font-size:0.82rem; color:#047857; margin:0; line-height:1.45;">Official ratification and release of final Semester 1 transcripts &amp; grade sheets.</p>
            </div>

            <!-- Milestone 6 -->
            <div style="background: rgba(5, 150, 105, 0.05); border: 1px solid rgba(5, 150, 105, 0.25); border-left: 5px solid #059669; border-radius: var(--radius-md); padding: 1.1rem;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.72rem; font-weight:800; color:#ffffff; background:#059669; padding:0.2rem 0.55rem; border-radius:4px;">NEXT SEM</span>
                <span style="font-size:0.75rem; font-weight:700; color:#059669;">23 January, 2027</span>
              </div>
              <h4 style="font-size:1rem; font-weight:800; color:#065f46; margin:0.5rem 0 0.25rem 0;">Spring Semester 2027 Starts</h4>
              <p style="font-size:0.82rem; color:#047857; margin:0; line-height:1.45;">First day of instruction for Semester 2 (Spring 2027 academic session).</p>
            </div>
          </div>
        </div>
      </div>

      <!-- SUB-PANE 4: Enrolled Subject Analytics & Syllabi -->
      <div class="sub-pane" id="analyticsSubPane">
        <div class="course-cards-grid" id="analyticsCardsGrid">
          <!-- Course analytics cards injected via JS -->
        </div>
      </div>
"""
    else:
        # Semester 2, 3, or 4 Upcoming Notice Content
        semester_body_html = f"""
      <!-- Selected Subjects Overview Banner -->
      <div class="sem-overview-card">
        <div class="sem-overview-header">
          <h2>
            <span>📚</span>
            <span>{sem_name} Selected Curriculum ({credits_num} Credits)</span>
          </h2>
          <span style="font-size:0.8rem; color:var(--text-secondary);">{period_str}</span>
        </div>
        {chips_grid_html}
      </div>

      <!-- Semester Not Begun Notice Banner -->
      <div class="upcoming-box" style="margin-top: 1.5rem; padding: 3rem 2rem;">
        <div class="upcoming-icon" style="font-size: 3rem;">⏳</div>
        <h2 style="font-size: 1.5rem; font-weight: 800; color: #1e1b4b; margin-bottom: 0.75rem;">
          Semester has not begun yet !!
        </h2>
        <p style="color: var(--text-secondary); font-size: 0.95rem; max-width: 650px; margin: 0 auto 1.5rem auto; line-height: 1.6;">
          Class schedule and attendance data for <strong>{sem_name}</strong> will be activated once the academic session begins as per the IIT Patna academic calendar. Your selected core subjects and electives are configured and saved above.
        </p>
        <div style="display:flex; justify-content:center; gap:0.75rem; flex-wrap: wrap;">
          <span class="badge-pill" style="font-size: 0.85rem; padding: 0.45rem 1rem;">Total Credits: {credits_num}</span>
          <span class="badge-pill" style="background: rgba(5, 150, 105, 0.12); color: #059669; font-size: 0.85rem; padding: 0.45rem 1rem; border-color: rgba(5, 150, 105, 0.3);">
            ✓ Selected Subjects Configured
          </span>
        </div>
      </div>
"""

    sem1_courses_json = json.dumps(user_sem1_courses, indent=6, ensure_ascii=False)
    all_courses_json = json.dumps(catalog, indent=2, ensure_ascii=False)

    logo_html = '<div class="institute-logo">ST</div>'
    if os.path.exists(LOGO_IMAGE_PATH):
        try:
            with open(LOGO_IMAGE_PATH, 'rb') as img_f:
                logo_b64 = base64.b64encode(img_f.read()).decode('utf-8')
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="StudyTrac Logo" style="height:48px; width:auto; max-width:64px; object-fit:contain; border-radius:6px; flex-shrink:0;">'
        except Exception:
            pass

    full_html = f"""<!DOCTYPE html>
<html lang="en" data-theme="warm-white">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>StudyTrac • Academic &amp; Attendance Companion</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;

      /* Warm White Theme */
      --bg-primary: #faf7f2;
      --bg-secondary: #f4eee3;
      --bg-card: #ffffff;
      --bg-card-hover: #ffffff;
      --bg-input: #f3ece0;
      --border-color: rgba(68, 64, 60, 0.12);
      --border-focus: #4338ca;

      --text-primary: #1c1917;
      --text-secondary: #57534e;
      --text-muted: #78716c;

      --primary: #4338ca;
      --primary-hover: #3730a3;
      --primary-light: rgba(67, 56, 202, 0.08);

      --accent-blue: #0284c7;
      --accent-purple: #9333ea;
      --accent-amber: #d97706;
      --accent-emerald: #059669;
      --accent-rose: #e11d48;
      --accent-cyan: #0891b2;

      --core-color: #0284c7;
      --core-bg: rgba(2, 132, 199, 0.09);
      --core-border: rgba(2, 132, 199, 0.28);

      --elec-color: #d97706;
      --elec-bg: rgba(217, 119, 6, 0.09);
      --elec-border: rgba(217, 119, 6, 0.28);

      --proj-color: #9333ea;
      --proj-bg: rgba(147, 51, 234, 0.09);
      --proj-border: rgba(147, 51, 234, 0.28);

      --shadow-sm: 0 2px 8px rgba(68, 64, 60, 0.05);
      --shadow-md: 0 8px 24px rgba(68, 64, 60, 0.08);
      --shadow-glow: 0 0 25px rgba(67, 56, 202, 0.10);

      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 18px;
      --radius-full: 9999px;

      --transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font-main);
      background-color: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      line-height: 1.5;
      background-image:
        radial-gradient(circle at 10% 12%, rgba(217, 119, 6, 0.035) 0%, transparent 45%),
        radial-gradient(circle at 90% 88%, rgba(67, 56, 202, 0.035) 0%, transparent 45%);
      background-attachment: fixed;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: var(--bg-primary);
    }}
    ::-webkit-scrollbar-thumb {{
      background: #e2d9cc;
      border-radius: var(--radius-full);
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: var(--text-muted);
    }}

    .app-container {{
      max-width: 1780px;
      width: 96%;
      margin: 0 auto;
      padding: 1.25rem 1.5rem 4rem 1.5rem;
    }}

    /* Header */
    .navbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 1.5rem;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      margin-bottom: 1.25rem;
      box-shadow: var(--shadow-sm);
    }}

    .brand-section {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    .institute-logo {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: linear-gradient(135deg, #312e81, #4338ca);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.2rem;
      color: #fff;
      box-shadow: 0 4px 12px rgba(67, 56, 202, 0.25);
    }}

    .brand-details h1 {{
      font-size: 1.2rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #1e1b4b;
    }}

    .brand-details p {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      font-weight: 500;
      margin-top: 2px;
    }}

    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .badge-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.4rem 0.85rem;
      border-radius: var(--radius-full);
      font-size: 0.78rem;
      font-weight: 600;
      background: rgba(5, 150, 105, 0.08);
      color: #059669;
      border: 1px solid rgba(5, 150, 105, 0.25);
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.55rem 1rem;
      border-radius: var(--radius-md);
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-primary);
      transition: var(--transition);
      user-select: none;
    }}

    .btn:hover {{
      background: var(--bg-secondary);
      border-color: rgba(68, 64, 60, 0.25);
      transform: translateY(-1px);
    }}

    .btn-primary {{
      background: linear-gradient(135deg, #4338ca, #3730a3);
      color: #ffffff;
      border-color: #3730a3;
      box-shadow: 0 4px 14px rgba(67, 56, 202, 0.25);
    }}

    .btn-primary:hover {{
      background: linear-gradient(135deg, #3730a3, #312e81);
    }}

    .btn-sm {{
      padding: 0.35rem 0.75rem;
      font-size: 0.75rem;
      border-radius: var(--radius-sm);
    }}

    /* Selected Semester Header Banner */
    .sem-header-banner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.15rem 1.5rem;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-left: 5px solid var(--primary);
      border-radius: var(--radius-lg);
      margin-bottom: 1.5rem;
      box-shadow: var(--shadow-sm);
    }}

    .sem-header-left h2 {{
      font-size: 1.25rem;
      font-weight: 800;
      color: #1e1b4b;
      margin-bottom: 0.2rem;
    }}

    .sem-header-left p {{
      font-size: 0.82rem;
      color: var(--text-secondary);
    }}

    /* Selected Subjects Overview Banner */
    .sem-overview-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: var(--shadow-sm);
    }}

    .sem-overview-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border-color);
    }}

    .sem-overview-header h2 {{
      font-size: 1.15rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      color: #1e1b4b;
    }}

    /* Symmetrical 5-Column Grid */
    .subject-chips-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 0.85rem;
    }}

    @media (max-width: 1200px) {{
      .subject-chips-grid {{
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      }}
    }}

    .subject-chip {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 0.85rem 1rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.4rem;
      transition: var(--transition);
      cursor: pointer;
    }}

    .subject-chip:hover {{
      background: #ffffff;
      border-color: var(--primary);
      box-shadow: var(--shadow-sm);
      transform: translateY(-2px);
    }}

    .chip-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .chip-title {{
      font-weight: 700;
      font-size: 0.88rem;
      color: var(--text-primary);
      line-height: 1.35;
    }}

    .chip-faculty {{
      font-size: 0.75rem;
      color: var(--text-secondary);
    }}

    .clickable-cue {{
      font-size: 0.7rem;
      font-weight: 700;
      color: var(--primary);
      margin-top: 0.25rem;
    }}

    .course-tag {{
      font-size: 0.68rem;
      font-weight: 700;
      padding: 0.18rem 0.5rem;
      border-radius: var(--radius-full);
      text-transform: uppercase;
      font-family: var(--font-mono);
    }}

    .course-tag-core {{
      background: var(--core-bg);
      color: var(--core-color);
      border: 1px solid var(--core-border);
    }}

    .course-tag-elec {{
      background: var(--elec-bg);
      color: var(--elec-color);
      border: 1px solid var(--elec-border);
    }}

    .course-tag-proj {{
      background: var(--proj-bg);
      color: var(--proj-color);
      border: 1px solid var(--proj-border);
    }}

    /* Sub-tabs for Semester 1 */
    .sub-tabs-nav {{
      display: flex;
      gap: 0.5rem;
      padding: 0.35rem;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      margin-bottom: 1.5rem;
      overflow-x: auto;
      box-shadow: var(--shadow-sm);
    }}

    .sub-tab-btn {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.65rem 1.1rem;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      font-size: 0.85rem;
      font-weight: 600;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: var(--transition);
      white-space: nowrap;
    }}

    .sub-tab-btn:hover {{
      color: var(--text-primary);
      background: var(--bg-secondary);
    }}

    .sub-tab-btn.active {{
      background: var(--primary);
      color: #ffffff;
      box-shadow: 0 4px 14px rgba(67, 56, 202, 0.25);
    }}

    /* Symmetrical 5-Column Stats Grid */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 0.85rem;
      margin-bottom: 1.5rem;
    }}

    @media (max-width: 1200px) {{
      .stats-grid {{
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      }}
    }}

    .stat-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.15rem 1.25rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.4rem;
      box-shadow: var(--shadow-sm);
      transition: var(--transition);
    }}

    .stat-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(68, 64, 60, 0.25);
      box-shadow: var(--shadow-md);
    }}

    .stat-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .stat-title {{
      font-size: 0.78rem;
      color: var(--text-secondary);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .stat-icon-wrap {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--primary-light);
      color: var(--primary);
      font-size: 0.95rem;
    }}

    .stat-value {{
      font-size: 1.85rem;
      font-weight: 800;
      font-family: var(--font-mono);
      letter-spacing: -0.03em;
      line-height: 1.1;
      margin-top: 0.2rem;
    }}

    .stat-meta {{
      font-size: 0.75rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .status-indicator {{
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }}

    .status-good {{ background-color: var(--accent-emerald); }}
    .status-warning {{ background-color: var(--accent-amber); }}
    .status-danger {{ background-color: var(--accent-rose); }}

    .threshold-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.25rem 0.6rem;
      border-radius: var(--radius-sm);
      font-size: 0.72rem;
      font-weight: 700;
    }}

    .threshold-pass {{
      background: rgba(5, 150, 105, 0.12);
      color: #059669;
      border: 1px solid rgba(5, 150, 105, 0.25);
    }}

    .threshold-fail {{
      background: rgba(225, 29, 72, 0.12);
      color: #e11d48;
      border: 1px solid rgba(225, 29, 72, 0.25);
    }}

    /* Today's Schedule Card */
    .today-banner {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: var(--shadow-sm);
    }}

    .today-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border-color);
    }}

    .today-header h3 {{
      font-size: 1.05rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: #1e1b4b;
    }}

    .today-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1rem;
    }}

    .today-item {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 1rem 1.25rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.85rem;
      border-left: 4px solid var(--primary);
    }}

    .today-item-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.35rem;
    }}

    .today-item-title {{
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--text-primary);
    }}

    .today-item-faculty {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-top: 0.2rem;
    }}

    .today-item-time {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: #0284c7;
      font-weight: 700;
      background: rgba(2, 132, 199, 0.08);
      padding: 0.2rem 0.55rem;
      border-radius: var(--radius-sm);
      border: 1px solid rgba(2, 132, 199, 0.2);
    }}

    .attendance-actions {{
      display: flex;
      gap: 0.4rem;
      align-items: center;
      flex-wrap: wrap;
    }}

    .btn-status {{
      padding: 0.35rem 0.7rem;
      border-radius: var(--radius-sm);
      font-size: 0.75rem;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid var(--border-color);
      background: #ffffff;
      color: var(--text-secondary);
      transition: var(--transition);
    }}

    .btn-status:hover {{
      background: #f4eee3;
      border-color: rgba(68, 64, 60, 0.25);
    }}

    .btn-status.active-live {{
      background: #059669;
      color: #ffffff;
      border-color: #059669;
    }}

    .btn-status.active-rec {{
      background: #0284c7;
      color: #ffffff;
      border-color: #0284c7;
    }}

    .btn-status.active-cancelled, .btn-status.active-absent {{
      background: #ea580c;
      color: #ffffff;
      border-color: #ea580c;
    }}

    /* Join Button Styling */
    .btn-join {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.35rem 0.75rem;
      font-size: 0.78rem;
      font-weight: 700;
      color: #ffffff !important;
      background: linear-gradient(135deg, #4338ca, #6366f1);
      border: 1px solid #4338ca;
      border-radius: var(--radius-sm);
      text-decoration: none;
      box-shadow: 0 2px 5px rgba(67, 56, 202, 0.2);
      transition: var(--transition);
      white-space: nowrap;
    }}

    .btn-join:hover {{
      background: linear-gradient(135deg, #3730a3, #4f46e5);
      transform: translateY(-1px);
      box-shadow: 0 4px 10px rgba(67, 56, 202, 0.3);
      color: #ffffff !important;
    }}

    .btn-table-join {{
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      padding: 0.22rem 0.55rem;
      font-size: 0.72rem;
      font-weight: 700;
      color: #4338ca !important;
      background: rgba(67, 56, 202, 0.08);
      border: 1px solid rgba(67, 56, 202, 0.25);
      border-radius: var(--radius-sm);
      text-decoration: none;
      transition: var(--transition);
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .btn-table-join:hover {{
      background: #4338ca;
      color: #ffffff !important;
      border-color: #4338ca;
      box-shadow: 0 2px 6px rgba(67, 56, 202, 0.25);
    }}

    /* Sub-pane animations */
    .sub-pane {{
      display: none;
      animation: fadeIn 0.25s ease;
    }}

    .sub-pane.active {{
      display: block;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Controls Bar */
    .controls-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.25rem;
      flex-wrap: wrap;
    }}

    .search-input-wrap {{
      position: relative;
      flex: 1;
      min-width: 260px;
    }}

    .search-input {{
      width: 100%;
      padding: 0.65rem 1rem 0.65rem 2.5rem;
      background: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      color: var(--text-primary);
      font-size: 0.85rem;
      outline: none;
      transition: var(--transition);
    }}

    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(67, 56, 202, 0.12);
    }}

    .search-icon {{
      position: absolute;
      left: 0.85rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
    }}

    .filters-group {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      align-items: center;
    }}

    .select-dropdown {{
      padding: 0.6rem 1rem;
      background: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      color: var(--text-primary);
      font-size: 0.82rem;
      outline: none;
      cursor: pointer;
      transition: var(--transition);
    }}

    .select-dropdown:focus {{
      border-color: var(--primary);
    }}

    /* Schedule & Timetable Tables */
    .schedule-table-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: var(--shadow-sm);
      margin-bottom: 1.5rem;
    }}

    .table-responsive {{
      width: 100%;
      overflow-x: auto;
    }}

    .custom-table {{
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.82rem;
    }}

    .custom-table th {{
      background: #f4eee3;
      color: #1c1917;
      padding: 0.85rem 1rem;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 0.72rem;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--border-color);
      white-space: nowrap;
    }}

    .custom-table td {{
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--border-color);
      vertical-align: middle;
    }}

    .custom-table tr:hover td {{
      background: rgba(68, 64, 60, 0.025);
    }}

    .custom-table tr.row-attended-live td {{ background: rgba(5, 150, 105, 0.04); }}
    .custom-table tr.row-attended-rec td {{ background: rgba(2, 132, 199, 0.04); }}
    .custom-table tr.row-cancelled td, .custom-table tr.row-absent td {{ background: rgba(234, 88, 12, 0.05); }}

    .date-cell {{
      font-family: var(--font-mono);
      font-weight: 600;
      white-space: nowrap;
    }}

    .time-slot-pill {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: #0284c7;
      background: rgba(2, 132, 199, 0.08);
      padding: 0.2rem 0.55rem;
      border-radius: var(--radius-sm);
      border: 1px solid rgba(2, 132, 199, 0.2);
      white-space: nowrap;
      display: inline-block;
    }}

    .course-cell-title {{
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 2px;
    }}

    .course-cell-sub {{
      font-size: 0.75rem;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .week-header-row {{
      cursor: pointer;
      user-select: none;
      transition: background 0.15s ease;
    }}

    .week-header-row td {{
      background: #f4eee3 !important;
      font-weight: 800;
      font-size: 0.85rem;
      color: #1e1b4b;
      padding: 0.65rem 1rem;
      border-top: 2px solid var(--primary);
    }}

    .week-header-row:hover td {{
      background: #eae0d2 !important;
    }}

    /* Timetable Grid with Equal Width for All 8 Columns */
    .timetable-grid-wrap {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      overflow-x: auto;
      box-shadow: var(--shadow-sm);
      margin-bottom: 1.5rem;
    }}

    .timetable-table {{
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      min-width: 800px;
    }}

    .timetable-table th {{
      background: #f4eee3;
      padding: 0.75rem 0.5rem;
      font-size: 0.75rem;
      font-weight: 700;
      text-align: center;
      border-bottom: 1px solid var(--border-color);
      border-right: 1px solid var(--border-color);
      color: #1c1917;
      width: 12.5% !important;
      box-sizing: border-box;
    }}

    .timetable-table td {{
      width: 12.5% !important;
      box-sizing: border-box;
      border: 1px solid var(--border-color);
      padding: 0.5rem;
      vertical-align: top;
      min-height: 60px;
    }}

    .timetable-table td.time-col {{
      background: #f4eee3;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-secondary);
      text-align: center;
      width: 12.5% !important;
      vertical-align: middle;
    }}

    .grid-course-card {{
      padding: 0.55rem;
      border-radius: var(--radius-sm);
      font-size: 0.75rem;
      margin-bottom: 0.35rem;
    }}

    .grid-card-core {{
      background: rgba(2, 132, 199, 0.08);
      border: 1px solid rgba(2, 132, 199, 0.25);
      border-left: 3px solid #0284c7;
    }}

    .grid-card-elec {{
      background: rgba(217, 119, 6, 0.08);
      border: 1px solid rgba(217, 119, 6, 0.25);
      border-left: 3px solid #d97706;
    }}

    .grid-card-code {{
      font-weight: 800;
      font-family: var(--font-mono);
      margin-bottom: 2px;
    }}

    .grid-card-name {{
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 2px;
      line-height: 1.2;
    }}

    .grid-card-meta {{
      font-size: 0.65rem;
      color: var(--text-muted);
    }}

    /* Course Cards Grid */
    .course-cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.25rem;
    }}

    .course-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 1rem;
      box-shadow: var(--shadow-sm);
      transition: var(--transition);
    }}

    .course-card:hover {{
      border-color: var(--primary);
      box-shadow: var(--shadow-md);
      transform: translateY(-2px);
    }}

    .course-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .course-card-title {{
      font-size: 1rem;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .progress-bar-wrap {{
      width: 100%;
      height: 8px;
      background: #f4eee3;
      border-radius: var(--radius-full);
      overflow: hidden;
      margin: 0.5rem 0;
    }}

    .progress-bar-fill {{
      height: 100%;
      border-radius: var(--radius-full);
      background: var(--accent-emerald);
      transition: width 0.5s ease;
    }}

    .progress-bar-fill.danger {{ background: var(--accent-rose); }}
    .progress-bar-fill.warning {{ background: var(--accent-amber); }}

    .course-card-stats {{
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      color: var(--text-secondary);
      font-family: var(--font-mono);
    }}

    /* Upcoming Semester Box */
    .upcoming-box {{
      background: var(--bg-card);
      border: 1px dashed rgba(68, 64, 60, 0.25);
      border-radius: var(--radius-lg);
      padding: 2.5rem 2rem;
      text-align: center;
      margin-top: 1.5rem;
    }}

    .upcoming-icon {{
      font-size: 2.5rem;
      margin-bottom: 0.75rem;
    }}

    .upcoming-box h3 {{
      font-size: 1.25rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      color: #1e1b4b;
    }}

    .upcoming-box p {{
      color: var(--text-secondary);
      font-size: 0.9rem;
      max-width: 600px;
      margin: 0 auto 1.5rem auto;
    }}

    /* Modal Styling */
    .modal-overlay {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(28, 25, 23, 0.55);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.25rem;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.22s ease, visibility 0.22s ease;
    }}

    .modal-overlay.active {{
      opacity: 1;
      visibility: visible;
    }}

    .course-modal-dialog {{
      background: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      width: 100%;
      max-width: 820px;
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      overflow: hidden;
    }}

    .course-modal-header {{
      padding: 1.25rem 1.5rem;
      background: #f4eee3;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
    }}

    .course-modal-title {{
      font-size: 1.3rem;
      font-weight: 800;
      color: #1e1b4b;
      margin: 0.35rem 0 0.2rem 0;
      line-height: 1.25;
    }}

    .course-modal-meta {{
      font-size: 0.82rem;
      color: var(--text-secondary);
      font-family: var(--font-mono);
      font-weight: 600;
    }}

    .course-modal-close {{
      background: #ffffff;
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1rem;
      font-weight: 700;
      transition: var(--transition);
      flex-shrink: 0;
    }}

    .course-modal-close:hover {{
      background: var(--accent-rose);
      color: #ffffff;
      border-color: var(--accent-rose);
    }}

    .course-modal-body {{
      padding: 1.5rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }}

    .modal-section {{
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}

    .modal-section-header {{
      font-size: 0.92rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #1e1b4b;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding-bottom: 0.35rem;
      border-bottom: 1px solid var(--border-color);
    }}

    .modal-desc-box {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 0.9rem 1.1rem;
      font-size: 0.9rem;
      line-height: 1.6;
      color: var(--text-primary);
    }}

    .objectives-list {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 0.5rem;
    }}

    .objective-item {{
      display: flex;
      align-items: flex-start;
      gap: 0.65rem;
      background: rgba(5, 150, 105, 0.06);
      border: 1px solid rgba(5, 150, 105, 0.2);
      border-radius: var(--radius-md);
      padding: 0.65rem 0.85rem;
      font-size: 0.85rem;
      color: var(--text-primary);
      line-height: 1.45;
    }}

    .objective-icon {{
      color: var(--accent-emerald);
      font-weight: 800;
      flex-shrink: 0;
      margin-top: 1px;
    }}

    .outline-timeline {{
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .outline-module {{
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 0.75rem 1rem;
      font-size: 0.84rem;
      line-height: 1.5;
    }}

    .outline-badge {{
      background: var(--primary);
      color: #ffffff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-sm);
      flex-shrink: 0;
      margin-top: 2px;
      font-family: var(--font-mono);
    }}

    .books-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 0.75rem;
    }}

    .book-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 0.85rem 1rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.5rem;
    }}

    .book-title {{
      font-weight: 700;
      font-size: 0.88rem;
      color: var(--text-primary);
      line-height: 1.35;
    }}

    .book-author {{
      font-size: 0.8rem;
      color: var(--text-secondary);
    }}

    .book-meta {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.75rem;
      color: var(--text-muted);
      font-family: var(--font-mono);
      padding-top: 0.35rem;
      border-top: 1px dashed var(--border-color);
    }}

    .book-type-badge {{
      font-size: 0.68rem;
      font-weight: 700;
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-sm);
      text-transform: uppercase;
    }}

    .book-type-textbook {{
      background: rgba(67, 56, 202, 0.12);
      color: #4338ca;
      border: 1px solid rgba(67, 56, 202, 0.25);
    }}

    /* Enhanced Mobile, Tablet & Multi-Screen Responsiveness */
    @media (max-width: 1024px) {{
      .app-container {{
        width: 98%;
        padding: 1rem;
      }}
      .attendance-hero-grid {{
        grid-template-columns: 1fr;
        gap: 1.25rem;
      }}
      .stat-metric-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}

    @media (max-width: 768px) {{
      .app-container {{
        width: 100%;
        padding: 0.75rem 0.5rem;
      }}
      .navbar {{
        flex-direction: column;
        gap: 0.85rem;
        padding: 0.85rem 1rem;
        text-align: center;
      }}
      .brand-section {{
        flex-direction: column;
        gap: 0.5rem;
      }}
      .brand-details h1 {{
        font-size: 1.05rem;
      }}
      .nav-actions {{
        width: 100%;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.5rem;
      }}
      .sem-header-banner {{
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 1rem;
      }}
      .sem-header-badges {{
        width: 100%;
        display: flex;
        justify-content: flex-start;
        flex-wrap: wrap;
      }}
      .sub-tabs-nav {{
        display: flex;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
        gap: 0.4rem;
        scrollbar-width: thin;
      }}
      .sub-tab-btn {{
        flex-shrink: 0;
        white-space: nowrap;
        padding: 0.5rem 0.85rem;
        font-size: 0.8rem;
      }}
      .controls-bar {{
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
        padding: 0.85rem;
      }}
      .controls-group {{
        flex-direction: column;
        width: 100%;
        gap: 0.5rem;
      }}
      .control-select, .control-search {{
        width: 100%;
      }}

      /* Mobile Card Transformation for Schedule Table */
      .schedule-table-card {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 1rem !important;
      }}

      .table-responsive {{
        overflow: visible !important;
      }}

      .custom-table,
      .custom-table tbody,
      .custom-table tr,
      .custom-table td {{
        display: block !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }}

      .custom-table thead {{
        display: none !important; /* Hide cramped table headers on phone screens */
      }}

      .week-header-row {{
        display: block !important;
        margin-top: 1.1rem !important;
        margin-bottom: 0.6rem !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid var(--border-color) !important;
      }}

      .week-header-row td {{
        display: block !important;
        width: 100% !important;
        padding: 0.85rem 1rem !important;
      }}

      /* Each session transforms into a stacked Mobile Card */
      .custom-table tbody tr:not(.week-header-row) {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        margin-bottom: 0.75rem !important;
        padding: 0.9rem 1rem !important;
        box-shadow: 0 2px 6px rgba(68, 64, 60, 0.04) !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 0.45rem !important;
      }}

      .custom-table tbody tr:not(.week-header-row) td {{
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
      }}

      /* Date Cell (Header of the mobile card) */
      .custom-table tbody tr:not(.week-header-row) td:nth-child(1) {{
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding-bottom: 0.4rem !important;
        border-bottom: 1px dashed var(--border-color) !important;
      }}

      /* Time Slot Pill */
      .custom-table tbody tr:not(.week-header-row) td:nth-child(2) {{
        margin-top: -0.1rem !important;
      }}

      /* Course Details & Faculty */
      .custom-table tbody tr:not(.week-header-row) td:nth-child(3) {{
        padding: 0.2rem 0 !important;
      }}

      .course-cell-title {{
        font-size: 0.95rem !important;
        line-height: 1.35 !important;
      }}

      .course-cell-sub {{
        flex-wrap: wrap !important;
        gap: 0.35rem !important;
        font-size: 0.75rem !important;
      }}

      /* Attendance Actions */
      .custom-table tbody tr:not(.week-header-row) td:nth-child(4) {{
        padding-top: 0.45rem !important;
        border-top: 1px solid rgba(68, 64, 60, 0.08) !important;
      }}

      .attendance-actions {{
        display: flex !important;
        width: 100% !important;
        gap: 0.35rem !important;
      }}

      .btn-status {{
        flex: 1 !important;
        text-align: center !important;
        padding: 0.45rem 0.2rem !important;
        font-size: 0.76rem !important;
      }}

      /* Notes */
      .custom-table tbody tr:not(.week-header-row) td:nth-child(5) {{
        padding-top: 0.15rem !important;
      }}

      .course-cards-grid, .calendar-cards-grid {{
        grid-template-columns: 1fr !important;
      }}
      .course-modal-dialog {{
        width: 95% !important;
        margin: 0.5rem auto !important;
        max-height: 92vh !important;
      }}
      .course-modal-header {{
        padding: 0.85rem 1rem !important;
      }}
      .course-modal-body {{
        padding: 0.85rem 1rem !important;
      }}
      .books-grid {{
        grid-template-columns: 1fr !important;
      }}
    }}

    @media (max-width: 480px) {{
      .schedule-table {{
        min-width: 560px;
      }}
      .hero-gauge-box {{
        padding: 1rem !important;
      }}
      .hero-gauge-pct {{
        font-size: 2.2rem !important;
      }}
      .stat-metric-card {{
        padding: 0.75rem !important;
      }}
      .stat-metric-val {{
        font-size: 1.4rem !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="app-container">
    <!-- Top Navigation Header -->
    <header class="navbar">
      <div class="brand-section">
        {logo_html}
        <div class="brand-details">
          <h1>StudyTrac</h1>
          <p>Academic &amp; Attendance Companion • Curated for IIT Patna M.Tech (AI &amp; Data Science)</p>
        </div>
      </div>
      <div class="nav-actions">
        <span class="badge-pill">
          <span class="status-indicator status-good"></span>
          Mandatory 75% Attendance
        </span>
        <span class="badge-pill" style="background: rgba(67, 56, 202, 0.08); color: var(--primary); border-color: rgba(67, 56, 202, 0.25);">
          Total: 84 Credits
        </span>
      </div>
    </header>

    <!-- Selected Semester Banner -->
    <div class="sem-header-banner">
      <div class="sem-header-left">
        <h2>🎓 {sem_name} Selected Curriculum ({credits_num} Credits)</h2>
        <p>{period_str}</p>
      </div>
      <div class="sem-header-badges">
        <span class="badge-pill" style="font-weight: 700;">{badge_str}</span>
      </div>
    </div>

    <!-- Active Semester Content -->
    {semester_body_html}

    <!-- Footer Signature -->
    <footer style="margin-top: 3.5rem; padding: 2rem 1rem 1.5rem 1rem; text-align: center; border-top: 1px solid var(--border-color); color: var(--text-secondary); font-size: 0.85rem; font-weight: 500;">
      Crafted with ❤️ by <strong style="color: #000000;">Shivam Bhatt</strong> | IIT Patna (Batch 2026–2028)
    </footer>

    <!-- COURSE SYLLABUS & DETAILS MODAL DIALOG -->
    <div class="modal-overlay" id="courseModalOverlay" onclick="handleModalOverlayClick(event)">
      <div class="course-modal-dialog">
        <div class="course-modal-header">
          <div>
            <span class="course-tag course-tag-core" id="modalCourseTag">CORE</span>
            <h3 class="course-modal-title" id="modalCourseTitle">Course Name</h3>
            <div class="course-modal-meta" id="modalCourseMeta">4 Credits • 3-0-2-4</div>
          </div>
          <button class="course-modal-close" onclick="closeCourseModal()" title="Close (Esc)">✕</button>
        </div>
        <div class="course-modal-body">
          <!-- Course Description -->
          <div class="modal-section">
            <div class="modal-section-header"><span>📖</span> Course Overview</div>
            <div class="modal-desc-box" id="modalCourseDescription">...</div>
          </div>
          <!-- Learning Objectives -->
          <div class="modal-section">
            <div class="modal-section-header"><span>🎯</span> Key Learning Objectives</div>
            <div class="objectives-list" id="modalCourseObjectives">...</div>
          </div>
          <!-- Detailed Outline -->
          <div class="modal-section">
            <div class="modal-section-header"><span>📋</span> Syllabus Outline &amp; Modules</div>
            <div class="outline-timeline" id="modalCourseOutline">...</div>
          </div>
          <!-- Prescribed Books -->
          <div class="modal-section">
            <div class="modal-section-header"><span>📚</span> Prescribed Textbooks &amp; Reference Materials</div>
            <div class="books-grid" id="modalCourseBooks">...</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notes Modal Dialog -->
    <div class="modal-overlay" id="noteModalOverlay" onclick="handleNoteModalOverlayClick(event)">
      <div class="course-modal-dialog" style="max-width: 550px;">
        <div class="course-modal-header">
          <div>
            <h3 class="course-modal-title" id="noteModalTitle" style="font-size: 1.15rem;">Class Notes</h3>
            <div class="course-modal-meta" id="noteModalSubtitle">...</div>
          </div>
          <button class="course-modal-close" onclick="closeNoteModal()" title="Close">✕</button>
        </div>
        <div class="course-modal-body" style="padding: 1.25rem;">
          <textarea id="noteModalTextarea" style="width: 100%; height: 160px; padding: 0.85rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); font-family: var(--font-main); font-size: 0.88rem; outline: none; resize: vertical;" placeholder="Type your personal preparation notes, assignment reminders, or questions for the professor..."></textarea>
          <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem;">
            <button class="btn btn-sm" onclick="closeNoteModal()">Cancel</button>
            <button class="btn btn-sm btn-primary" onclick="saveActiveModalNote()">💾 Save Note</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    /**
     * IIT PATNA M.TECH (AI & DATA SCIENCE) ACCURATE CURRICULUM CONFIGURATION
     */
    const ACTIVE_SEMESTER_NUM = {active_semester};
    const USER_SEM1_COURSES = {sem1_courses_json};
    const ALL_COURSES_DATA = {all_courses_json};

    const SEM1_START_DATE = "2026-08-16";
    const SEM1_END_DATE = "2026-11-30";
    const TOTAL_WEEKS = 16;
    const STORAGE_ATTENDANCE_KEY = "iitp_mtech_attendance_v2";
    const STORAGE_NOTES_KEY = "iitp_mtech_notes_v2";

    const DAYS_OF_WEEK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const HOLIDAYS_MAP = {holidays_json};

    const EXAM_RESULT_TIMELINE = [
      {{
        dateRange: "01 Dec – 30 Dec 2026",
        dayLabel: "Weekends (Sat & Sun)",
        timeSlot: "Proctored Online",
        title: "End Semester Examination (ESE)",
        description: "Mandatory Proctored Online Mode • 50% Official Course Weightage",
        tag: "50% ESE",
        badge: "Proctored Exam",
        note: "All 5 Enrolled Subjects"
      }},
      {{
        dateRange: "10 January 2027",
        dayLabel: "Sunday",
        timeSlot: "Faculty Deadline",
        title: "Project Grade Submission",
        description: "Last date for department faculty submission of project & lab evaluation grades",
        tag: "GRADING",
        badge: "Faculty Submission",
        note: "Department Evaluation"
      }},
      {{
        dateRange: "20 January 2027",
        dayLabel: "Wednesday",
        timeSlot: "Academic Portal",
        title: "Declaration of Provisional Results",
        description: "Provisional Semester 1 Performance & Grade Reports Published on Portal",
        tag: "RESULTS",
        badge: "Results Out",
        note: "Provisional Publication"
      }},
      {{
        dateRange: "21 January 2027",
        dayLabel: "Thursday",
        timeSlot: "Student Window",
        title: "Grade Revision Claim Window",
        description: "Last date for student submission of grade revision or re-evaluation requests",
        tag: "REVISION",
        badge: "Student Window",
        note: "Re-evaluation Claims"
      }},
      {{
        dateRange: "22 January 2027",
        dayLabel: "Friday",
        timeSlot: "Official Record",
        title: "Final Result Declaration",
        description: "Official ratification and release of final Semester 1 transcripts & grade cards",
        tag: "FINAL GRADES",
        badge: "Official Transcript",
        note: "Semester 1 Completed"
      }},
      {{
        dateRange: "23 January 2027",
        dayLabel: "Saturday",
        timeSlot: "Next Semester",
        title: "First Day of Instruction for Spring Semester 2026-27",
        description: "Commencement of Semester 2 Live & Recorded Lectures",
        tag: "SEM 2 START",
        badge: "New Semester",
        note: "Spring 2027 Begins"
      }}
    ];

    let generatedSessions = [];
    let attendanceRecords = {{}};
    let classNotes = {{}};
    let collapsedWeeks = {{}};
    let activeEditingSessionId = null;

    // Default all 16 weeks and exams to collapsed initially
    for (let w = 1; w <= TOTAL_WEEKS; w++) {{
      collapsedWeeks[w] = true;
    }}
    collapsedWeeks["exams"] = true;

    function toggleWeekCollapse(weekNum) {{
      collapsedWeeks[weekNum] = !collapsedWeeks[weekNum];
      renderTrackerTable();
    }}

    function toggleCollapseAll() {{
      const anyExpanded = Object.values(collapsedWeeks).some(v => v === false);
      for (let w = 1; w <= TOTAL_WEEKS; w++) {{
        collapsedWeeks[w] = anyExpanded;
      }}
      collapsedWeeks["exams"] = anyExpanded;
      renderTrackerTable();
    }}

    function openCourseModal(courseCode) {{
      const overlay = document.getElementById("courseModalOverlay");
      if (!overlay) return;

      const cleanCode = String(courseCode).toLowerCase().replace(/[^a-z0-9]/g, '');
      const course = ALL_COURSES_DATA.find(c => {{
        const cCode = String(c.subject_code || '').toLowerCase().replace(/[^a-z0-9]/g, '');
        const cName = String(c.subject_name || '').toLowerCase().replace(/[^a-z0-9]/g, '');
        return cCode === cleanCode || cCode.includes(cleanCode) || cleanCode.includes(cCode) || cName.includes(cleanCode);
      }});

      if (!course) {{
        alert("Syllabus details for " + courseCode + " will be updated shortly.");
        return;
      }}

      document.getElementById("modalCourseTitle").textContent = course.subject_name || courseCode;
      document.getElementById("modalCourseMeta").textContent = (course.credits || "3 Credits") + " • Semester " + (course.semester || "Curriculum");

      const tagEl = document.getElementById("modalCourseTag");
      const ctype = (course.course_type || "CORE").toUpperCase();
      tagEl.textContent = `${{ctype}} • ${{course.subject_code}}`;
      tagEl.className = ctype.includes("ELEC") ? "course-tag course-tag-elec" : (ctype.includes("PROJ") ? "course-tag course-tag-proj" : "course-tag course-tag-core");

      document.getElementById("modalCourseDescription").textContent = course.description || "Course details and curriculum overview.";

      const objList = document.getElementById("modalCourseObjectives");
      objList.innerHTML = "";
      if (course.learning_objectives && course.learning_objectives.length > 0) {{
        course.learning_objectives.forEach(obj => {{
          const item = document.createElement("div");
          item.className = "objective-item";
          item.innerHTML = `<span class="objective-icon">✓</span><span>${{obj}}</span>`;
          objList.appendChild(item);
        }});
      }} else {{
        objList.innerHTML = `<div style="color:var(--text-muted); font-size:0.85rem;">Learning outcomes and competencies outlined by faculty.</div>`;
      }}

      const outlineList = document.getElementById("modalCourseOutline");
      outlineList.innerHTML = "";
      if (course.outline && course.outline.length > 0) {{
        course.outline.forEach((mod, idx) => {{
          const item = document.createElement("div");
          item.className = "outline-module";
          item.innerHTML = `<span class="outline-badge">Module ${{idx + 1}}</span><span>${{mod}}</span>`;
          outlineList.appendChild(item);
        }});
      }} else {{
        outlineList.innerHTML = `<div style="color:var(--text-muted); font-size:0.85rem;">Detailed week-by-week topic breakdown to be announced.</div>`;
      }}

      const booksList = document.getElementById("modalCourseBooks");
      booksList.innerHTML = "";
      if (course.books && course.books.length > 0) {{
        course.books.forEach(b => {{
          const card = document.createElement("div");
          card.className = "book-card";
          const isText = (b.type || "").toLowerCase().includes("text");
          card.innerHTML = `
            <div>
              <div class="book-title">${{b.title || "Untitled"}}</div>
              <div class="book-author">✍ ${{b.author || "Unknown Author"}}</div>
            </div>
            <div class="book-meta">
              <span>${{b.publisher || ""}} ${{b.edition_year ? "(" + b.edition_year + ")" : ""}}</span>
              <span class="book-type-badge ${{isText ? "book-type-textbook" : "book-type-reference"}}">${{b.type || "Reference"}}</span>
            </div>
          `;
          booksList.appendChild(card);
        }});
      }} else {{
        booksList.innerHTML = `<div style="color:var(--text-muted); font-size:0.85rem; grid-column:1/-1;">Prescribed references and lecture handouts will be distributed on Moodle.</div>`;
      }}

      overlay.classList.add("active");
      document.body.style.overflow = "hidden";
    }}

    function closeCourseModal() {{
      const overlay = document.getElementById("courseModalOverlay");
      if (overlay) overlay.classList.remove("active");
      document.body.style.overflow = "";
    }}

    function handleModalOverlayClick(e) {{
      if (e.target.id === "courseModalOverlay") closeCourseModal();
    }}

    function switchSubTab(targetId, btn) {{
      document.querySelectorAll(".sub-pane").forEach(p => p.classList.remove("active"));
      document.querySelectorAll(".sub-tab-btn").forEach(b => b.classList.remove("active"));
      const target = document.getElementById(targetId);
      if (target) target.classList.add("active");
      if (btn) btn.classList.add("active");
    }}

    function formatDateISO(date) {{
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, '0');
      const d = String(date.getDate()).padStart(2, '0');
      return `${{y}}-${{m}}-${{d}}`;
    }}

    function formatDateDisplay(isoStr) {{
      const [y, m, d] = isoStr.split("-");
      const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      return `${{d}} ${{months[parseInt(m, 10) - 1]}} ${{y}}`;
    }}

    function generateSemester1Schedule() {{
      const sessions = [];
      let currentDate = new Date(2026, 7, 16);
      const endDate = new Date(2026, 10, 30);
      let sessionIndex = 1;

      while (currentDate <= endDate) {{
        const iso = formatDateISO(currentDate);
        const dayOfWeek = currentDate.getDay();
        const holidayReason = HOLIDAYS_MAP[iso] || null;

        const diffDays = Math.floor((currentDate - new Date(2026, 7, 16)) / (1000 * 60 * 60 * 24));
        const weekNumber = Math.floor(diffDays / 7) + 1;

        let hasSlots = false;
        USER_SEM1_COURSES.forEach(course => {{
          course.slots.forEach((slot, slotIdx) => {{
            if (slot.day === dayOfWeek) {{
              hasSlots = true;
              sessions.push({{
                id: `sess_${{iso}}_${{course.code.replace(/[^a-zA-Z0-9]/g, '')}}_${{slotIdx}}`,
                dateStr: iso,
                dayName: DAYS_OF_WEEK[dayOfWeek],
                weekNumber: weekNumber,
                timeLabel: slot.label,
                courseCode: course.code,
                courseName: course.name,
                courseType: course.type,
                credits: course.credits,
                faculty: course.faculty,
                color: course.color,
                isHoliday: !!holidayReason,
                holidayReason: holidayReason,
                sequenceIndex: sessionIndex++
              }});
            }}
          }});
        }});

        if (holidayReason && !hasSlots) {{
          sessions.push({{
            id: `holiday_${{iso}}`,
            dateStr: iso,
            dayName: DAYS_OF_WEEK[dayOfWeek],
            weekNumber: weekNumber,
            timeLabel: "All Day",
            courseCode: "HOLIDAY",
            courseName: "Institute Holiday",
            courseType: "HOLIDAY",
            credits: "-",
            faculty: "IIT Patna",
            color: "#64748b",
            isHoliday: true,
            holidayReason: holidayReason,
            sequenceIndex: sessionIndex++
          }});
        }}

        currentDate.setDate(currentDate.getDate() + 1);
      }}

      return sessions;
    }}

    function renderAttendanceStats() {{
      const nonHolidaySessions = generatedSessions.filter(s => !s.isHoliday && s.courseCode !== 'HOLIDAY');
      const totalSemesterSessions = nonHolidaySessions.length;
      let attendedLive = 0, attendedRec = 0, cancelledCount = 0, totalMarked = 0;

      nonHolidaySessions.forEach(s => {{
        const status = attendanceRecords[s.id];
        if (status === 'live') {{ attendedLive++; totalMarked++; }}
        else if (status === 'rec') {{ attendedRec++; totalMarked++; }}
        else if (status === 'cancelled' || status === 'absent') {{ cancelledCount++; }}
      }});

      const totalAttended = attendedLive + attendedRec;
      const effectiveSemesterSessions = Math.max(1, totalSemesterSessions - cancelledCount);
      // Cancellation by faculty is not an unexcused absence; attendance compliance is based on conducted sessions
      const currentPct = totalMarked > 0 ? ((totalAttended / totalMarked) * 100) : 100;
      const maxAllowedBunks = Math.floor(effectiveSemesterSessions * 0.25);

      const elAtt = document.getElementById("statAttendedCount");
      if (elAtt) elAtt.textContent = totalAttended;
      const elBk = document.getElementById("statAttendedBreakdown");
      if (elBk) elBk.textContent = `Live: ${{attendedLive}} | Rec: ${{attendedRec}}`;
      const elCan = document.getElementById("statCancelledCount") || document.getElementById("statMissedCount");
      if (elCan) elCan.textContent = cancelledCount;
      const elPast = document.getElementById("statTotalPastClasses");
      if (elPast) elPast.textContent = totalAttended;
      const elSem = document.getElementById("statTotalSemesterClasses");
      if (elSem) elSem.textContent = `of ${{effectiveSemesterSessions}} active sessions`;
      const elBunk = document.getElementById("statBunksAllowed");
      if (elBunk) elBunk.textContent = maxAllowedBunks;

      const displayPct = totalMarked > 0 ? (Math.round(currentPct * 10) / 10) : 100;
      const elGaugePct = document.getElementById("heroGaugePct");
      if (elGaugePct) {{
        elGaugePct.textContent = `${{displayPct}}%`;
        elGaugePct.style.color = (totalMarked === 0) ? "var(--accent-emerald)" : (currentPct >= 75 ? "var(--accent-emerald)" : "var(--accent-rose)");
      }}

      const heroStatus = document.getElementById("heroAttendanceStatus");
      if (heroStatus) {{
        if (totalMarked === 0) {{
          heroStatus.innerHTML = '<span class="status-indicator status-good"></span> Ready (100% Policy Compliant)';
          heroStatus.style.color = "var(--accent-emerald)";
        }} else if (currentPct >= 75) {{
          heroStatus.innerHTML = '<span class="status-indicator status-good"></span> ≥ 75% Compliant';
          heroStatus.style.color = "var(--accent-emerald)";
        }} else {{
          heroStatus.innerHTML = '<span class="status-indicator status-danger"></span> Below 75% Alert';
          heroStatus.style.color = "var(--accent-rose)";
        }}
      }}
    }}

    function setupTodayHeader() {{
      const el = document.getElementById("todayHeaderDate");
      if (!el) return;
      const now = new Date();
      const dayName = DAYS_OF_WEEK[now.getDay()];
      const dateStr = formatDateDisplay(formatDateISO(now));
      el.textContent = `Today (${{dayName}}, ${{dateStr}})`;
    }}

    function renderTodayClasses() {{
      const listContainer = document.getElementById("todayScheduleList");
      if (!listContainer) return;
      listContainer.innerHTML = "";

      const now = new Date();
      const todayISO = formatDateISO(now);
      const todayClasses = generatedSessions.filter(s => s.dateStr === todayISO);
      const badge = document.getElementById("todayClassesCountBadge");
      if (badge) badge.textContent = `${{todayClasses.length}} Class(es) Scheduled`;

      if (todayClasses.length === 0) {{
        listContainer.innerHTML = `
          <div style="grid-column: 1 / -1; padding: 2rem; text-align: center; color: var(--text-muted); background: var(--bg-secondary); border-radius: var(--radius-md); border: 1px dashed var(--border-color);">
            <p style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">No classes scheduled for today.</p>
            <p style="font-size: 0.85rem; margin-top: 0.35rem; color: var(--text-secondary);">Instruction period: August 16 – November 30, 2026.</p>
          </div>
        `;
        return;
      }}

      todayClasses.forEach(session => {{
        const status = attendanceRecords[session.id] || "unmarked";
        const item = document.createElement("div");
        item.className = "today-item";

        if (session.isHoliday) {{
          item.style.background = "#f1f5f9";
          item.style.borderColor = "#cbd5e1";
          item.innerHTML = `
            <div>
              <div class="today-item-top">
                <span class="course-tag" style="background:#e2e8f0; color:#475569; border-color:#cbd5e1;">${{session.courseCode}}</span>
                <span class="today-item-time" style="background:#e2e8f0; color:#64748b;">⏰ ${{session.timeLabel}}</span>
              </div>
              <h4 class="today-item-title" style="color:#475569; text-decoration:${{session.courseCode === 'HOLIDAY' ? 'none' : 'line-through'}}; text-decoration-color:#94a3b8;">${{session.courseName}}</h4>
              <div style="font-size:0.82rem; font-weight:700; color:#475569; margin-top:0.25rem;">
                🏖️ No Class: ${{session.holidayReason}} (Institute Holiday)
              </div>
            </div>
            <div style="display:flex; align-items:center;">
              <span style="font-size:0.8rem; font-weight:700; color:#475569; background:#e2e8f0; padding:0.35rem 0.8rem; border-radius:6px; border:1px solid #cbd5e1;">
                🏖️ Off Day
              </span>
            </div>
          `;
          listContainer.appendChild(item);
          return;
        }}

        item.innerHTML = `
          <div>
            <div class="today-item-top">
              <span class="course-tag ${{session.courseType === 'CORE' ? 'course-tag-core' : 'course-tag-elec'}}">${{session.courseCode}}</span>
              <span class="today-item-time">⏰ ${{session.timeLabel}}</span>
            </div>
            <h4 class="today-item-title">${{session.courseName}}</h4>
            <div class="today-item-faculty">👤 ${{session.faculty}} • <span style="color:var(--text-muted);">${{session.credits}}</span></div>
          </div>
          <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
            <a href="https://cetpgex.iitp.ac.in/moodle/login/index.php" target="_blank" rel="noopener noreferrer" class="btn-join" title="Join live class on IIT Patna Moodle">
              <span>🚀 Join Class</span>
            </a>
            <div class="attendance-actions">
              <button class="btn-status ${{status === 'live' ? 'active-live' : ''}}" onclick="setAttendanceStatus('${{session.id}}', 'live')" title="Attended Live">✅ Live</button>
              <button class="btn-status ${{status === 'rec' ? 'active-rec' : ''}}" onclick="setAttendanceStatus('${{session.id}}', 'rec')" title="Attended Recorded">🎥 Recorded</button>
              <button class="btn-status ${{status === 'cancelled' || status === 'absent' ? 'active-cancelled' : ''}}" onclick="setAttendanceStatus('${{session.id}}', 'cancelled')" title="Class Cancelled by Faculty">🚫 Cancel</button>
              <button class="btn-status" onclick="setAttendanceStatus('${{session.id}}', 'unmarked')" title="Clear">⚪</button>
            </div>
          </div>
        `;
        listContainer.appendChild(item);
      }});
    }}

    function markAllTodayAttended(type) {{
      const now = new Date();
      const todayISO = formatDateISO(now);
      generatedSessions.forEach(s => {{
        if (s.dateStr === todayISO && !s.isHoliday) attendanceRecords[s.id] = type;
      }});
      saveAttendanceState();
      renderAllViews();
    }}

    function setAttendanceStatus(sessionId, status) {{
      if (status === 'unmarked') delete attendanceRecords[sessionId];
      else attendanceRecords[sessionId] = status;
      saveAttendanceState();
      renderAllViews();
    }}

    function saveAttendanceState() {{
      try {{
        localStorage.setItem(STORAGE_ATTENDANCE_KEY, JSON.stringify(attendanceRecords));
      }} catch (e) {{
        console.warn("Storage save error:", e);
      }}
    }}

    function saveClassNote(sessionId, text) {{
      if (!text) delete classNotes[sessionId];
      else classNotes[sessionId] = text;
      try {{
        localStorage.setItem(STORAGE_NOTES_KEY, JSON.stringify(classNotes));
      }} catch (e) {{
        console.warn("Storage save error:", e);
      }}
    }}

    function renderTrackerTable() {{
      const tbody = document.getElementById("trackerTableBody");
      if (!tbody) return;
      tbody.innerHTML = "";

      const weekFilter = document.getElementById("filterWeek") ? document.getElementById("filterWeek").value : "all";
      const courseFilter = document.getElementById("filterCourse") ? document.getElementById("filterCourse").value : "all";
      const statusFilter = document.getElementById("filterStatus") ? document.getElementById("filterStatus").value : "all";
      const searchInput = document.getElementById("classSearchInput");
      const searchQuery = searchInput ? searchInput.value.trim().toLowerCase() : "";

      let filtered = generatedSessions.filter(s => {{
        if (weekFilter !== "all" && s.weekNumber !== parseInt(weekFilter, 10)) return false;
        if (courseFilter !== "all" && s.courseCode !== courseFilter) return false;
        if (statusFilter !== "all") {{
          const st = attendanceRecords[s.id] || "unmarked";
          if (statusFilter === 'cancelled') {{
            if (st !== 'cancelled' && st !== 'absent') return false;
          }} else if (st !== statusFilter) {{
            return false;
          }}
        }}
        return true;
      }});

      if (searchQuery) {{
        filtered = filtered.filter(s =>
          s.courseName.toLowerCase().includes(searchQuery) ||
          s.courseCode.toLowerCase().includes(searchQuery) ||
          s.faculty.toLowerCase().includes(searchQuery) ||
          s.dateStr.includes(searchQuery) ||
          (s.holidayReason && s.holidayReason.toLowerCase().includes(searchQuery))
        );
      }}

      if (filtered.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--text-muted);">No class sessions match the filter criteria.</td></tr>`;
        return;
      }}

      let currentWeek = null;
      filtered.forEach(session => {{
        if (session.weekNumber !== currentWeek) {{
          currentWeek = session.weekNumber;
          const weekNum = currentWeek;
          const isCollapsed = !!collapsedWeeks[weekNum];
          const weekCount = filtered.filter(s => s.weekNumber === weekNum).length;

          const weekHeader = document.createElement("tr");
          weekHeader.className = "week-header-row";
          weekHeader.onclick = () => toggleWeekCollapse(weekNum);
          weekHeader.innerHTML = `
            <td colspan="5" style="cursor: pointer;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="display:inline-flex; align-items:center; gap:0.5rem; font-weight:800; font-size:0.88rem;">
                  <span>${{isCollapsed ? '▶' : '▼'}}</span>
                  <span>📅 Week ${{weekNum}}</span>
                  <span style="font-size:0.75rem; font-weight:600; color:var(--text-secondary);">(${{weekCount}} Sessions)</span>
                </span>
                <span style="font-size:0.72rem; font-weight:700; color:var(--primary); background:rgba(67,56,202,0.1); padding:0.2rem 0.55rem; border-radius:4px;">
                  ${{isCollapsed ? 'Click to Expand ▾' : 'Click to Collapse ▴'}}
                </span>
              </div>
            </td>
          `;
          tbody.appendChild(weekHeader);
        }}

        if (collapsedWeeks[session.weekNumber]) return;

        const note = classNotes[session.id] || "";

        if (session.isHoliday) {{
          const row = document.createElement("tr");
          row.style.background = "#f1f5f9";
          row.style.color = "#475569";
          row.style.borderBottom = "1px solid #e2e8f0";
          row.innerHTML = `
            <td class="date-cell">
              <div style="font-weight:700; color:#475569;">${{formatDateDisplay(session.dateStr)}}</div>
              <div style="font-size:0.75rem; color:#94a3b8;">${{session.dayName}}</div>
            </td>
            <td>
              <span class="time-slot-pill" style="background:#e2e8f0; color:#64748b; border:1px solid #cbd5e1; font-weight:600;">
                ${{session.timeLabel}}
              </span>
            </td>
            <td>
              <div class="course-cell-title" style="color:#475569; text-decoration:${{session.courseCode === 'HOLIDAY' ? 'none' : 'line-through'}}; text-decoration-color:#94a3b8;">
                ${{session.courseName}}
              </div>
              <div class="course-cell-sub" style="color:#64748b; margin-top:0.25rem;">
                <span class="course-tag" style="background:#e2e8f0; color:#475569; border-color:#cbd5e1;">${{session.courseCode}}</span>
                <span style="font-weight:700; color:#475569; background:#e2e8f0; padding:0.18rem 0.55rem; border-radius:4px; font-size:0.74rem;">
                  🏖️ No Class: ${{session.holidayReason}}
                </span>
              </div>
            </td>
            <td>
              <span style="font-size:0.76rem; font-weight:700; color:#475569; background:#e2e8f0; padding:0.3rem 0.65rem; border-radius:6px; border:1px solid #cbd5e1; display:inline-flex; align-items:center; gap:0.3rem;">
                🏖️ Off Day (${{session.holidayReason}})
              </span>
            </td>
            <td>
              <button class="btn btn-sm" onclick="openNoteModal('${{session.id}}')" style="font-size:0.75rem; width:100%; justify-content:flex-start; text-overflow:ellipsis; overflow:hidden; background:#e2e8f0; color:#64748b; border:1px solid #cbd5e1;">
                📝 ${{note ? note : "Holiday Notes..."}}
              </button>
            </td>
          `;
          tbody.appendChild(row);
          return;
        }}

        const status = attendanceRecords[session.id] || "unmarked";
        const row = document.createElement("tr");
        if (status === 'live') row.className = "row-attended-live";
        else if (status === 'rec') row.className = "row-attended-rec";
        else if (status === 'cancelled' || status === 'absent') row.className = "row-cancelled";

        row.innerHTML = `
          <td class="date-cell">
            <div style="font-weight:700;">${{formatDateDisplay(session.dateStr)}}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">${{session.dayName}}</div>
          </td>
          <td><span class="time-slot-pill">${{session.timeLabel}}</span></td>
          <td>
            <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.25rem; flex-wrap:wrap;">
              <a href="https://cetpgex.iitp.ac.in/moodle/login/index.php" target="_blank" rel="noopener noreferrer" class="btn-table-join" title="Join session on IIT Patna Moodle">
                <span>🔗 Join</span>
              </a>
              <span class="course-cell-title">${{session.courseName}}</span>
            </div>
            <div class="course-cell-sub">
              <span class="course-tag ${{session.courseType === 'CORE' ? 'course-tag-core' : 'course-tag-elec'}}">${{session.courseCode}}</span>
              <span>👤 ${{session.faculty}}</span>
            </div>
          </td>
          <td>
            <div class="attendance-actions">
              <button class="btn-status ${{status === 'live' ? 'active-live' : ''}}" onclick="setAttendanceStatus('${{session.id}}', 'live')" title="Attended Live">Live</button>
              <button class="btn-status ${{status === 'rec' ? 'active-rec' : ''}}" onclick="setAttendanceStatus('${{session.id}}', 'rec')" title="Attended Recorded">Rec</button>
              <button class="btn-status ${{status === 'cancelled' || status === 'absent' ? 'active-cancelled' : ''}}" onclick="setAttendanceStatus('${{session.id}}', 'cancelled')" title="Faculty Cancellation">Cancel</button>
              <button class="btn-status" onclick="setAttendanceStatus('${{session.id}}', 'unmarked')" title="Clear">⚪</button>
            </div>
          </td>
          <td>
            <button class="btn btn-sm" onclick="openNoteModal('${{session.id}}')" style="font-size:0.75rem; width:100%; justify-content:flex-start; text-overflow:ellipsis; overflow:hidden;">
              📝 ${{note ? note : "Add Note..."}}
            </button>
          </td>
        `;
        tbody.appendChild(row);
      }});

      if (weekFilter === "all" || weekFilter === "exams") {{
        const isExamCollapsed = !!collapsedWeeks["exams"];
        const examHeader = document.createElement("tr");
        examHeader.className = "week-header-row";
        examHeader.style.background = "linear-gradient(90deg, rgba(5, 150, 105, 0.14), rgba(5, 150, 105, 0.04))";
        examHeader.style.borderLeft = "5px solid #059669";
        examHeader.onclick = () => {{
          collapsedWeeks["exams"] = !collapsedWeeks["exams"];
          renderTrackerTable();
        }};
        examHeader.innerHTML = `
          <td colspan="5" style="cursor: pointer; padding: 0.85rem 1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="display:inline-flex; align-items:center; gap:0.5rem; font-weight:800; font-size:0.9rem; color:#065f46;">
                <span>${{isExamCollapsed ? '▶' : '▼'}}</span>
                <span>🎓 Post-Instruction Timeline: End Semester Exams &amp; Result Declaration (Dec 2026 – Jan 2027)</span>
                <span style="font-size:0.75rem; font-weight:700; color:#059669; background:rgba(5,150,105,0.15); padding:0.15rem 0.55rem; border-radius:4px;">(6 Key Milestones)</span>
              </span>
              <span style="font-size:0.72rem; font-weight:700; color:#059669; background:rgba(5,150,105,0.15); padding:0.2rem 0.6rem; border-radius:4px;">
                ${{isExamCollapsed ? 'Click to Expand ▾' : 'Click to Collapse ▴'}}
              </span>
            </div>
          </td>
        `;
        tbody.appendChild(examHeader);

        if (!isExamCollapsed) {{
          EXAM_RESULT_TIMELINE.forEach((milestone, mIdx) => {{
            const mRow = document.createElement("tr");
            mRow.style.background = "rgba(5, 150, 105, 0.05)";
            mRow.style.borderLeft = "4px solid #059669";
            mRow.style.borderBottom = "1px solid rgba(5, 150, 105, 0.15)";
            mRow.innerHTML = `
              <td class="date-cell">
                <div style="font-weight:800; color:#065f46;">${{milestone.dateRange}}</div>
                <div style="font-size:0.75rem; color:#059669; font-weight:600;">${{milestone.dayLabel}}</div>
              </td>
              <td>
                <span class="time-slot-pill" style="background:rgba(5, 150, 105, 0.15); color:#065f46; border:1px solid rgba(5, 150, 105, 0.3); font-weight:700;">
                  ${{milestone.timeSlot}}
                </span>
              </td>
              <td>
                <div class="course-cell-title" style="color:#065f46; font-weight:800; font-size:0.95rem;">${{milestone.title}}</div>
                <div class="course-cell-sub" style="color:#047857; margin-top:0.25rem;">
                  <span class="course-tag" style="background:#059669; color:#ffffff; font-weight:700; border:none;">${{milestone.tag}}</span>
                  <span style="font-size:0.8rem; font-weight:600; color:#065f46;">${{milestone.description}}</span>
                </div>
              </td>
              <td>
                <span style="font-size:0.78rem; font-weight:800; color:#ffffff; background:#059669; padding:0.35rem 0.75rem; border-radius:6px; display:inline-flex; align-items:center; gap:0.35rem; box-shadow:0 2px 6px rgba(5,150,105,0.2);">
                  ✓ ${{milestone.badge}}
                </span>
              </td>
              <td>
                <div style="font-size:0.78rem; color:#065f46; font-weight:600; background:rgba(5,150,105,0.1); padding:0.4rem 0.6rem; border-radius:6px; border:1px solid rgba(5,150,105,0.2);">
                  📌 ${{milestone.note}}
                </div>
              </td>
            `;
            tbody.appendChild(mRow);
          }});
        }}
      }}

      const anyExpanded = Object.values(collapsedWeeks).some(v => v === false);
      const collapseBtn = document.getElementById("collapseAllBtn");
      if (collapseBtn) {{
        collapseBtn.innerHTML = anyExpanded ? "📂 Collapse All Weeks" : "📁 Expand All Weeks";
      }}
    }}

    function renderAnalyticsView() {{
      const container = document.getElementById("analyticsCardsGrid");
      if (!container) return;
      container.innerHTML = "";

      USER_SEM1_COURSES.forEach(course => {{
        const courseSessions = generatedSessions.filter(s => s.courseCode === course.code && !s.isHoliday);
        const total = courseSessions.length;
        let attended = 0;
        let cancelled = 0;
        courseSessions.forEach(s => {{
          const st = attendanceRecords[s.id];
          if (st === 'live' || st === 'rec') attended++;
          else if (st === 'cancelled' || st === 'absent') cancelled++;
        }});

        const effectiveTotal = Math.max(1, total - cancelled);
        const pct = effectiveTotal > 0 ? Math.round((attended / effectiveTotal) * 100) : 100;
        const card = document.createElement("div");
        card.className = "course-card";
        card.innerHTML = `
          <div>
            <div class="course-card-header">
              <span class="course-tag ${{course.type === 'CORE' ? 'course-tag-core' : 'course-tag-elec'}}">${{course.code}}</span>
              <span class="badge-credits">${{course.credits}}</span>
            </div>
            <h3 class="course-card-title" style="margin-top:0.5rem;">${{course.name}}</h3>
            <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.25rem;">👤 ${{course.faculty}}</div>
          </div>
          <div>
            <div class="progress-bar-wrap">
              <div class="progress-bar-fill ${{pct < 75 ? 'danger' : ''}}" style="width: ${{pct}}%;"></div>
            </div>
            <div class="course-card-stats">
              <span>Attendance: ${{pct}}%</span>
              <span>${{attended}} / ${{effectiveTotal}} Sessions ${{cancelled > 0 ? `(${{cancelled}} Cancelled)` : ''}}</span>
            </div>
            <div style="margin-top:0.85rem; display:flex; gap:0.5rem;">
              <a href="https://cetpgex.iitp.ac.in/moodle/login/index.php" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="flex:1; justify-content:center; background:linear-gradient(135deg, #4338ca, #6366f1); color:#ffffff; font-weight:700; border:none; text-decoration:none;">
                🚀 Join Class
              </a>
              <button class="btn btn-sm" onclick="openCourseModal('${{course.code}}')" style="flex:1.4; justify-content:center;">📖 Objectives &amp; Books</button>
            </div>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function populateFilterDropdowns() {{
      const weekSelect = document.getElementById("filterWeek");
      if (weekSelect) {{
        weekSelect.innerHTML = '<option value="all">📅 All Weeks (Week 1 – 16)</option>';
        for (let w = 1; w <= TOTAL_WEEKS; w++) {{
          const opt = document.createElement("option");
          opt.value = w;
          opt.textContent = `Week ${{w}}`;
          weekSelect.appendChild(opt);
        }}
        weekSelect.innerHTML += '<option value="exams">🎓 Exams &amp; Result Timeline (Dec 2026 – Jan 2027)</option>';
      }}

      const courseSelect = document.getElementById("filterCourse");
      if (courseSelect) {{
        courseSelect.innerHTML = '<option value="all">📚 All 5 Courses</option>';
        USER_SEM1_COURSES.forEach(c => {{
          const opt = document.createElement("option");
          opt.value = c.code;
          opt.textContent = `${{c.code}} - ${{c.name}}`;
          courseSelect.appendChild(opt);
        }});
      }}
    }}

    function openNoteModal(sessionId) {{
      activeEditingSessionId = sessionId;
      const session = generatedSessions.find(s => s.id === sessionId);
      if (!session) return;

      document.getElementById("noteModalTitle").textContent = `${{session.courseName}} Notes`;
      document.getElementById("noteModalSubtitle").textContent = `${{formatDateDisplay(session.dateStr)}} • ${{session.timeLabel}}`;
      document.getElementById("noteModalTextarea").value = classNotes[sessionId] || "";

      document.getElementById("noteModalOverlay").classList.add("active");
    }}

    function closeNoteModal() {{
      document.getElementById("noteModalOverlay").classList.remove("active");
      activeEditingSessionId = null;
    }}

    function handleNoteModalOverlayClick(e) {{
      if (e.target.id === "noteModalOverlay") closeNoteModal();
    }}

    function saveActiveModalNote() {{
      if (activeEditingSessionId) {{
        const text = document.getElementById("noteModalTextarea").value.trim();
        saveClassNote(activeEditingSessionId, text);
        closeNoteModal();
        renderTrackerTable();
      }}
    }}

    function renderAllViews() {{
      if (ACTIVE_SEMESTER_NUM === 1) {{
        renderAttendanceStats();
        renderTodayClasses();
        renderTrackerTable();
        renderAnalyticsView();
      }}
    }}

    // Initialization
    window.addEventListener("DOMContentLoaded", () => {{
      try {{
        const savedAtt = localStorage.getItem(STORAGE_ATTENDANCE_KEY);
        if (savedAtt) attendanceRecords = JSON.parse(savedAtt);
        const savedNotes = localStorage.getItem(STORAGE_NOTES_KEY);
        if (savedNotes) classNotes = JSON.parse(savedNotes);
      }} catch (e) {{
        console.warn("Storage load error:", e);
      }}

      if (ACTIVE_SEMESTER_NUM === 1) {{
        generatedSessions = generateSemester1Schedule();
        setupTodayHeader();
        populateFilterDropdowns();
        renderAllViews();
      }}
    }});

    document.addEventListener("keydown", e => {{
      if (e.key === "Escape") {{
        closeCourseModal();
        closeNoteModal();
      }}
    }});
  </script>
</body>
</html>"""
    return full_html


def run_curriculum_sync(config=MY_CURRICULUM_SELECTION, target_files=None, active_semester=1):
    """
    Master pipeline: Reads timetable & catalog, applies user selections, and generates index.html files.
    """
    timetable_file = os.path.join(ROOT_DIR, 'Classes', 'timetable_web.html')
    courses_file = os.path.join(ROOT_DIR, 'courses', 'all_courses.json')

    if target_files is None:
        target_files = [
            os.path.join(ROOT_DIR, 'output', 'index.html')
        ]

    print("\n" + "=" * 80)
    print("IIT PATNA M.TECH (AI & DATA SCIENCE) - CURRICULUM SYNC PIPELINE")
    print(f"[*] Active Semester     : Semester {active_semester}")
    print("=" * 80)

    # 0. On-Demand Live Timetable & Holiday Calendar Sync from Official Portal
    synced, sync_msg = synchronizer.fetch_live_timetable(target_file=timetable_file)
    print(f"[*] Timetable Sync     : {sync_msg}")

    holidays_file = os.path.join(ROOT_DIR, 'courses', 'holidays.json')
    synced_h, msg_h, holidays_map = synchronizer.fetch_live_holidays(target_file=holidays_file)
    print(f"[*] Holiday Sync       : {msg_h}")

    # 1. Load Catalog & Timetable
    catalog = synchronizer.load_courses_catalog(courses_file)
    timetable_data = synchronizer.parse_timetable_html(timetable_file)

    # 2. Resolve Semester 1 Elective
    sem1_elective_input = config.get("semester_1", {}).get("elective_1", "EAI 6103")
    sem1_elective_obj = resolve_course_data(sem1_elective_input, catalog)
    sem1_elective_code = sem1_elective_obj.get('subject_code', 'EAI 6103')

    print(f"[*] Semester 1 Elective : {sem1_elective_code} ({sem1_elective_obj.get('subject_name')})")
    print(f"[*] Semester 2 Electives: {config.get('semester_2', {}).get('electives', [])}")
    print(f"[*] Semester 3 Electives: {config.get('semester_3', {}).get('electives', [])}")
    print(f"[*] Semester 4 Electives: {config.get('semester_4', {}).get('electives', [])}")

    # 3. Generate Timetable Lecture Slots for Semester 1
    user_sem1_courses = synchronizer.generate_user_sem1_courses_js(timetable_data, sem1_elective_code, catalog)
    total_slots = sum(len(c['slots']) for c in user_sem1_courses)
    print(f"[*] Generated {len(user_sem1_courses)} courses with {total_slots} weekly lecture slots.")

    # 4. Generate Full Single-Semester Dashboard HTML with Synchronized Holidays
    full_html = render_full_dashboard_html(
        active_semester,
        config,
        catalog,
        timetable_data,
        user_sem1_courses,
        holidays_map=holidays_map
    )

    # 5. Write to Target HTML Files
    success = True
    for tf in target_files:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(tf)), exist_ok=True)
            with open(tf, 'w', encoding='utf-8') as f:
                f.write(full_html)
            print(f"[SUCCESS] Updated HTML dashboard: {tf}")
        except Exception as e:
            print(f"[FAILED] Could not update {tf}: {e}")
            success = False

    print("=" * 80 + "\n")
    return success


if __name__ == '__main__':
    run_curriculum_sync()
