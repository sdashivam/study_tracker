# 🎓 IIT Patna — M.Tech in Artificial Intelligence & Data Science
### *Academic Curriculum Planner, Live Class Schedule & Attendance Compliance Tracker*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![IIT Patna](https://img.shields.io/badge/IIT%20Patna-M.Tech%20AI%20%26%20DS-065f46.svg)](https://www.iitp.ac.in/)
[![License](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)

A high-performance, responsive academic management dashboard and curriculum planner developed specifically for learners of the **Executive/Hybrid M.Tech in Artificial Intelligence and Data Science** at the **Indian Institute of Technology Patna (IIT Patna)**.

---

## 🌟 Key Features

### 1. 🎓 Interactive Curriculum & Electives Selector
* **Multipage Streamlit Experience:** Switch seamlessly between the *Curriculum Selector* and *Academic Dashboard*.
* **Semesters 1 to 4 Full Catalog:** Complete syllabus, learning objectives, and textbook data for all 24 core and elective courses (84 Total Credits).
* **Elective Track Configuration:** Select approved electives (sorted by course code) while mandatory core subjects remain locked and validated.
* **Centered Apply Action:** Single-click curriculum generation pipeline with instant feedback.

### 2. 📅 Day-Wise Schedule & Dynamic Attendance Tracker
* **16-Week Instruction Timeline:** Date-by-date schedule spanning August 16 to November 30, 2026.
* **Dynamic Attendance Health Gauge:** Real-time computation of compliance ($\ge 75\%$ mandatory policy) with live vs. recorded lecture breakdowns and safe bunk counters.
* **One-Click Week Collapsing:** All 16 weeks default to collapsed view with a global `📁 Expand All / 📂 Collapse All` toggle.
* **Personal Notes per Session:** Persistent in-browser note-taking for every class slot.

### 3. 🏖️ Live Institute Holiday Calendar & Grey Off-Day Styling
* **Automated Holiday Sync:** Connects to the official IIT Patna holiday calendar portal with end-of-year rollover.
* **Explicit Reason Badges:** Classes falling on official holidays (*e.g., Gandhi Jayanti, Dussehra, Diwali, Chhath Puja*) are rendered in muted slate grey with `🏖️ No Class: <Reason>` badges.
* **No False Absence Penalties:** Holiday dates are excluded from missed attendance calculations.

### 4. 🎓 Post-Instruction Exam, Evaluation & Result Roadmap
* **Official Academic Calendar Integration:** Extracted directly from the official timetable schedule (`Classes/1sem_timetable.pdf`).
* **Emerald Green Section:** Dedicated timeline for December 2026 – January 2027:
  * **Dec 01 – Dec 30, 2026:** End Semester Examinations (ESE — 50% Weightage, Weekends Only).
  * **Jan 10, 2027:** Project Grade Submission deadline.
  * **Jan 20, 2027:** Declaration of Provisional Results.
  * **Jan 21, 2027:** Grade Revision Claim window.
  * **Jan 22, 2027:** Final Result Declaration.
  * **Jan 23, 2027:** Commencement of Spring Semester 2026–27.

### 5. 🔄 Live Portal Timetable Auto-Fetch
* **On-Demand Startup Check:** Automatically fetches the live timetable HTML from the IIT Patna portal on app startup (cached for 30 minutes).
* **Smart Interval Normalization:** Merges consecutive hourly slots (*e.g., 6–7 PM + 7–8 PM*) into single continuous sessions (*6:00 PM – 8:00 PM*).
* **Offline Resilience:** Gracefully falls back to local cache if network connectivity is unavailable.

---

## 📊 Evaluation & Grading Weightage Policy

| Component | Weightage | Description / Schedule |
|---|:---:|---|
| **Assignments & Homework** | **30%** | 4 Periodic Tasks (Sep 11–15, Sep 25–Oct 01, Oct 25–29, Nov 08–12) |
| **Quizzes & Tests** | **20%** | 2 Proctored Online Tests (Quiz 1: Oct 11–15 \| Quiz 2: Nov 22–26) |
| **End Semester Exam (ESE)** | **50%** | Proctored Online Examination (Dec 01 – Dec 30, 2026 • Weekends) |
| **Attendance Policy** | **$\ge$ 75%** | Mandatory attendance via Live sessions or LMS recorded views |

---

## 📁 Repository Structure

```plaintext
d:/IITP/
│
├── app.py                      # Root Streamlit multipage application (Navigation & UI)
├── requirements.txt            # Python dependencies (Streamlit, BeautifulSoup4, etc.)
├── README.md                   # Project documentation
│
├── src/                        # Core Python sync & generation pipelines
│   ├── main.py                 # Dashboard HTML generator & evaluation engine
│   ├── sync_timetable_and_courses.py # Live portal fetcher for timetable & holidays
│   └── generate_courses.py     # Course catalog parser
│
├── courses/                    # Course data & holiday catalogs
│   ├── all_courses.json        # 24 subjects catalog across Semesters 1 to 4
│   ├── holidays.json           # Auto-synced IIT Patna official holiday calendar
│   └── *.json                  # Individual course syllabus JSON files
│
├── Classes/                    # Reference documents & timetable assets
│   ├── 1sem_timetable.pdf      # Official Academic Calendar & Exam Timeline
│   ├── syllabus.pdf            # Complete M.Tech curriculum & syllabus document
│   └── timetable_web.html      # Local cached timetable grid from portal
│
├── output/                     # Production build artifacts
│   └── index.html              # Standalone interactive dashboard
│
└── .streamlit/
    └── config.toml             # Warm-white theme and layout configuration
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
* **Python 3.10+**
* Virtual environment tool (`venv` or `conda`)

### 2. Setup Virtual Environment
```bash
# Clone or navigate to the project directory
cd d:/IITP

# Create and activate virtual environment (Windows PowerShell)
python -m venv virtual
.\virtual\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
# Start the Streamlit application
streamlit run app.py
```
Open **`http://localhost:8501`** in your web browser.

### 4. Direct Curriculum Generation (Optional)
To generate or re-compile the standalone `output/index.html` dashboard directly from the command line:
```bash
python src/main.py
```

---

## 🛠️ Technology Stack
* **Frontend:** Streamlit 1.40+, HTML5, CSS3 (Warm White & High-Contrast Dark Mode), Vanilla JavaScript.
* **Backend:** Python 3.10+, BeautifulSoup4, `urllib.request`.
* **State Management & Persistence:** Browser `localStorage` (Attendance & Notes) + Streamlit `session_state`.
* **Deployment Compatibility:** Localhost, Streamlit Community Cloud, Docker.

---

## 👥 Department & Institution
* **Programme:** M.Tech in Artificial Intelligence and Data Science (Executive / Hybrid)
* **Institution:** [Indian Institute of Technology Patna](https://www.iitp.ac.in/), Bihta, Patna, Bihar – 801106
* **Academic Session:** Autumn 2026 – Spring 2028

---

## ✍️ Author & Maintainer
**Crafted with ❤️ by Shivam Bhatt | IIT Patna (Batch 2026–2028)**

>>>>>>> 2dbd364 (Initial commit: IIT Patna M.Tech (AI & Data Science) Study & Attendance Tracker)
