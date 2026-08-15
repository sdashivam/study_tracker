"""
=============================================================================
IIT Patna M.Tech (AI & Data Science) — Streamlit Multipage Application
=============================================================================
Page 1: 🎓 Curriculum & Electives Selector
Page 2: 📊 Academic Dashboard (Live Interactive Dashboard for Selected Semester)
=============================================================================
"""

import os
import sys
import json
import base64
from pathlib import Path
import streamlit as st

# Setup Root & Source Paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
COURSES_JSON_PATH = os.path.join(ROOT_DIR, 'courses', 'all_courses.json')
OUTPUT_HTML_PATH = os.path.join(ROOT_DIR, 'output', 'index.html')
TIMETABLE_FILE = os.path.join(ROOT_DIR, 'Classes', 'timetable_web.html')
HOLIDAYS_FILE = os.path.join(ROOT_DIR, 'courses', 'holidays.json')
LOGO_IMAGE_PATH = os.path.join(ROOT_DIR, 'image', 'logo.png')

st.set_page_config(
    page_title="IIT Patna M.Tech (AI & Data Science)",
    page_icon=LOGO_IMAGE_PATH if os.path.exists(LOGO_IMAGE_PATH) else "🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import sync_timetable_and_courses as synchronizer
import main

# Automatically check and fetch the live timetable and holiday calendar from IIT Patna portal on startup
@st.cache_data(ttl=1800)
def auto_sync_live_data():
    t_synced, t_msg = synchronizer.fetch_live_timetable(target_file=TIMETABLE_FILE)
    h_synced, h_msg, h_data = synchronizer.fetch_live_holidays(target_file=HOLIDAYS_FILE)
    return {
        "timetable_synced": t_synced,
        "timetable_msg": t_msg,
        "holidays_synced": h_synced,
        "holidays_msg": h_msg,
        "holidays_data": h_data
    }

_sync_status = auto_sync_live_data()

# Global Styling for Warm White Canvas & Solid Black High-Contrast Typography
CUSTOM_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
  
  html, body, .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #faf7f2 !important;
    color: #000000 !important;
  }

  .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], section.main {
    background-color: #faf7f2 !important;
  }

  /* Full Width Optimization for Laptop and Desktop Screens */
  .block-container, [data-testid="stMainBlockContainer"], [data-testid="block-container"], .main .block-container {
    max-width: 96% !important;
    width: 96% !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
  }

  /* Text elements */
  p, h1, h2, h3, h4, h5, h6, label, .stMarkdown p, [data-testid="stMarkdownContainer"] p {
    color: #000000 !important;
  }

  /* Metric cards */
  [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: #000000 !important;
  }
  
  [data-testid="stMetric"] {
    background: #ffffff !important;
    padding: 0.85rem 1rem !important;
    border-radius: 12px !important;
    border: 1px solid rgba(68, 64, 60, 0.18) !important;
    box-shadow: 0 2px 6px rgba(68, 64, 60, 0.04) !important;
  }

  /* Radio & Select inputs */
  div[role="radiogroup"] label {
    background: #ffffff !important;
    border: 1px solid rgba(68, 64, 60, 0.2) !important;
    border-radius: 10px !important;
    padding: 0.5rem 0.85rem !important;
    margin-right: 0.5rem !important;
  }

  div[role="radiogroup"] label p, div[role="radiogroup"] label span {
    color: #000000 !important;
    font-weight: 700 !important;
  }

  .stSelectbox label, .stMultiSelect label {
    color: #000000 !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
  }

  /* Expanders - Clean styling without breaking internal toggle icons */
  [data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid rgba(68, 64, 60, 0.18) !important;
    border-radius: 10px !important;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }

  [data-testid="stExpander"] summary {
    color: #000000 !important;
    font-weight: 700 !important;
  }

  [data-testid="stExpander"] summary p {
    color: #000000 !important;
    font-weight: 700 !important;
  }

  /* Tabs */
  button[data-baseweb="tab"] {
    color: #000000 !important;
    font-weight: 700 !important;
  }
  
  button[data-baseweb="tab"][aria-selected="true"] {
    color: #4338ca !important;
    border-bottom-color: #4338ca !important;
  }

  /* Completely hide Streamlit sidebar and toggle */
  [data-testid="stSidebar"], [data-testid="collapsedControl"], section[data-testid="stSidebar"] {
    display: none !important;
  }
  
  /* Banner Header */
  .banner-container {
    background: #ffffff;
    border: 1px solid rgba(68, 64, 60, 0.18);
    border-left: 6px solid #4338ca;
    padding: 1.25rem 1.5rem;
    border-radius: 14px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(68, 64, 60, 0.04);
  }

  .banner-container h1 {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0;
    color: #000000 !important;
  }

  .banner-container p {
    color: #44403c !important;
    margin: 0.25rem 0 0 0;
    font-size: 0.92rem;
    font-weight: 600;
  }

  /* Subject Cards */
  .core-card {
    background: #ffffff;
    border: 1px solid rgba(68, 64, 60, 0.18);
    border-left: 5px solid #0284c7;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 2px 8px rgba(68, 64, 60, 0.05);
  }

  .elective-card {
    background: #ffffff;
    border: 1px solid rgba(217, 119, 6, 0.35);
    border-left: 5px solid #d97706;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 2px 8px rgba(68, 64, 60, 0.05);
  }

  .project-card {
    background: #ffffff;
    border: 1px solid rgba(147, 51, 234, 0.35);
    border-left: 5px solid #9333ea;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 2px 8px rgba(68, 64, 60, 0.05);
  }

  .badge-locked {
    background: #f4eee3;
    color: #1c1917 !important;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    border: 1px solid rgba(68, 64, 60, 0.2);
  }

  .badge-elective {
    background: rgba(217, 119, 6, 0.12);
    color: #b45309 !important;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    border: 1px solid rgba(217, 119, 6, 0.3);
  }

  .badge-credits {
    background: #f4eee3;
    color: #1c1917 !important;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
  }

  /* Action Buttons - Green with White Font */
  .stButton > button, div[data-testid="stButton"] > button {
    background: #059669 !important;
    background-color: #059669 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.4rem !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 14px rgba(5, 150, 105, 0.25) !important;
    transition: all 0.2s ease !important;
  }
  
  .stButton > button:hover, div[data-testid="stButton"] > button:hover {
    background: #047857 !important;
    background-color: #047857 !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(5, 150, 105, 0.35) !important;
  }

  .stButton > button * {
    color: #ffffff !important;
  }

  /* Mobile & Tablet Screen Responsiveness */
  @media (max-width: 768px) {
    .block-container, [data-testid="stMainBlockContainer"], [data-testid="block-container"], .main .block-container {
      max-width: 100% !important;
      width: 100% !important;
      padding-left: 0.6rem !important;
      padding-right: 0.6rem !important;
      padding-top: 0.5rem !important;
      padding-bottom: 1.5rem !important;
    }

    .banner-container {
      padding: 0.85rem 1rem !important;
      border-radius: 10px !important;
      margin-bottom: 1rem !important;
    }

    .banner-container h1 {
      font-size: 1.15rem !important;
    }

    .banner-container p {
      font-size: 0.78rem !important;
    }

    div[role="radiogroup"] {
      display: flex !important;
      flex-direction: column !important;
      gap: 0.35rem !important;
    }

    div[role="radiogroup"] label {
      margin-right: 0 !important;
      width: 100% !important;
      padding: 0.45rem 0.75rem !important;
      font-size: 0.82rem !important;
    }

    .core-card {
      padding: 0.85rem !important;
      border-radius: 10px !important;
      margin-bottom: 0.6rem !important;
    }

    .core-card-title {
      font-size: 0.95rem !important;
    }

    [data-testid="stMetric"] {
      padding: 0.65rem 0.8rem !important;
    }

    .stButton > button, div[data-testid="stButton"] > button {
      width: 100% !important;
      font-size: 0.88rem !important;
      padding: 0.6rem 1rem !important;
    }
  }
</style>
"""


@st.cache_data
def load_courses_from_json_file():
    if not os.path.exists(COURSES_JSON_PATH):
        st.error(f"Error: Course catalog file not found at '{COURSES_JSON_PATH}'")
        return []
    with open(COURSES_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def render_course_card(course, card_type="core", locked=False):
    code = course.get('subject_code', 'N/A')
    name = course.get('subject_name', 'Untitled')
    credits_str = course.get('credits', '')
    desc = course.get('description', '')
    objectives = course.get('learning_objectives', [])
    outline = course.get('outline', [])
    books = course.get('books', [])

    if card_type == "core":
        card_class = "core-card"
        badge_html = '<span class="badge-locked">🔒 Locked Mandatory Core</span>'
    elif card_type == "project":
        card_class = "project-card"
        badge_html = '<span class="badge-locked">🔒 Mandatory Project Thesis</span>'
    else:
        card_class = "elective-card"
        badge_html = '<span class="badge-elective">⚡ Elective Subject Option</span>'

    st.markdown(f"""
    <div class="{card_class}">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
        <div>
          <span style="font-weight:800; font-size:0.95rem; color:#000000 !important; font-family:'JetBrains Mono', monospace;">{code}</span>
          {badge_html}
        </div>
        <span class="badge-credits">{credits_str}</span>
      </div>
      <h4 style="margin:0.4rem 0 0.2rem 0; font-size:1.05rem; font-weight:800; color:#000000 !important;">{name}</h4>
      <p style="margin:0; font-size:0.88rem; color:#000000 !important; line-height:1.45; font-weight:500;">{desc}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"📖 View Syllabus, Objectives & Reference Books for {code}"):
        sub1, sub2, sub3 = st.tabs(["🎯 Learning Objectives", "📋 Outline Modules", "📚 Reference Books"])
        
        with sub1:
            if objectives:
                for obj in objectives:
                    st.markdown(f"- ✅ {obj}")
            else:
                st.caption("No specific objectives listed.")

        with sub2:
            if outline:
                for idx, mod in enumerate(outline, 1):
                    st.markdown(f"**Module {idx}:** {mod}")
            else:
                st.caption("Outline to be announced by faculty.")

        with sub3:
            if books:
                for b in books:
                    b_type = b.get('type', 'Reference')
                    b_title = b.get('title', 'Unknown Title')
                    b_auth = b.get('author', 'Unknown Author')
                    b_pub = b.get('publisher', '')
                    b_yr = b.get('edition_year', '')
                    st.markdown(f"- **{b_title}** by *{b_auth}* ({b_pub}, {b_yr}) `[{b_type}]`")
            else:
                st.caption("No textbooks listed.")


# =============================================================================
# PAGE 1: CURRICULUM & ELECTIVES SELECTOR
# =============================================================================
def page_curriculum_selector():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # 1. Header Banner
    logo_html = '<div style="background:linear-gradient(135deg, #312e81, #4338ca); color:#ffffff; width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.2rem; flex-shrink:0;">IITP</div>'
    if os.path.exists(LOGO_IMAGE_PATH):
        try:
            with open(LOGO_IMAGE_PATH, 'rb') as img_f:
                logo_b64 = base64.b64encode(img_f.read()).decode('utf-8')
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="IIT Patna Logo" style="height:52px; width:auto; max-width:70px; object-fit:contain; border-radius:8px; flex-shrink:0;">'
        except Exception:
            pass

    st.markdown(f"""
    <div class="banner-container">
      <div style="display:flex; align-items:center; gap:1rem;">
        {logo_html}
        <div>
          <h1 style="font-size:1.5rem; font-weight:800; color:#000000 !important; margin:0; letter-spacing:-0.02em;">IIT Patna • M.Tech in AI &amp; Data Science</h1>
          <p style="color:#292524 !important; font-weight:600; margin:0.25rem 0 0 0; font-size:0.9rem;">Semester-wise Curriculum Selector &amp; Elective Management Portal</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    all_courses = load_courses_from_json_file()

    # Group courses by Semester and Type
    courses_by_sem = {1: {'core': [], 'elective': [], 'project': []},
                      2: {'core': [], 'elective': [], 'project': []},
                      3: {'core': [], 'elective': [], 'project': []},
                      4: {'core': [], 'elective': [], 'project': []}}

    for course in all_courses:
        sem = course.get('semester', 1)
        if sem not in courses_by_sem:
            courses_by_sem[sem] = {'core': [], 'elective': [], 'project': []}
        ctype = course.get('course_type', 'Core').lower()
        if 'core' in ctype:
            courses_by_sem[sem]['core'].append(course)
        elif 'project' in ctype:
            courses_by_sem[sem]['project'].append(course)
        else:
            courses_by_sem[sem]['elective'].append(course)

    ELECTIVE_LIMITS = {1: 1, 2: 2, 3: 2, 4: 2}

    # Session State Initialization
    for s in [1, 2, 3, 4]:
        state_key = f"selected_electives_sem_{s}"
        if state_key not in st.session_state:
            avail = courses_by_sem[s]['elective']
            limit = ELECTIVE_LIMITS[s]
            default_selected = [c['subject_code'] for c in avail[:limit]]
            st.session_state[state_key] = default_selected

    # Semester Selection Banner
    st.markdown("### 📌 Select Academic Semester")
    semester_map = {
        "🎓 Semester 1 (Autumn 2026)": 1,
        "🎓 Semester 2 (Spring 2027)": 2,
        "🎓 Semester 3 (Autumn 2027)": 3,
        "🎓 Semester 4 (Spring 2028)": 4
    }

    current_sem_idx = st.session_state.get("active_semester", 1) - 1
    selected_sem_banner = st.radio(
        label="Semester Selection Banner",
        options=list(semester_map.keys()),
        horizontal=True,
        label_visibility="collapsed",
        index=current_sem_idx
    )

    selected_sem = semester_map.get(selected_sem_banner, 1)
    st.session_state["active_semester"] = selected_sem
    sem_data = courses_by_sem.get(selected_sem, {'core': [], 'elective': [], 'project': []})
    required_elective_count = ELECTIVE_LIMITS.get(selected_sem, 1)

    st.divider()

    # Two-Column Layout (Core Subjects on Left, Elective Selections on Right)
    col_core, col_elec = st.columns([1, 1], gap="large")

    with col_core:
        st.markdown(f"### 🔒 Mandatory Core Subjects (Semester {selected_sem})")
        st.caption("Core subjects are fixed by IIT Patna curriculum and remain locked.")

        if sem_data['core']:
            for course in sem_data['core']:
                render_course_card(course, card_type="core", locked=True)

        if sem_data['project']:
            for course in sem_data['project']:
                render_course_card(course, card_type="project", locked=True)

    with col_elec:
        st.markdown(f"### ⚡ Elective Selections (Select exactly {required_elective_count})")
        st.caption(f"Choose from the approved elective pool for Semester {selected_sem}:")

        available_electives = sorted(sem_data['elective'], key=lambda c: c.get('subject_code', ''))
        elective_options = {c['subject_code']: f"{c['subject_code']} - {c['subject_name']}" for c in available_electives}
        current_state_key = f"selected_electives_sem_{selected_sem}"

        if required_elective_count == 1:
            current_val = st.session_state[current_state_key][0] if st.session_state[current_state_key] else available_electives[0]['subject_code']
            if current_val not in elective_options:
                current_val = list(elective_options.keys())[0]

            selected_code = st.selectbox(
                label=f"Choose 1 Elective for Semester {selected_sem}:",
                options=list(elective_options.keys()),
                format_func=lambda x: elective_options[x],
                index=list(elective_options.keys()).index(current_val),
                key=f"widget_sem_{selected_sem}"
            )
            st.session_state[current_state_key] = [selected_code]

        else:
            current_vals = [v for v in st.session_state[current_state_key] if v in elective_options]
            if not current_vals:
                current_vals = list(elective_options.keys())[:required_elective_count]

            selected_codes = st.multiselect(
                label=f"Choose exactly {required_elective_count} Electives for Semester {selected_sem}:",
                options=list(elective_options.keys()),
                default=current_vals,
                format_func=lambda x: elective_options[x],
                max_selections=required_elective_count,
                key=f"widget_sem_{selected_sem}"
            )
            if len(selected_codes) == required_elective_count:
                st.session_state[current_state_key] = selected_codes
            else:
                st.warning(f"⚠️ Please select exactly {required_elective_count} electives (Currently selected: {len(selected_codes)}).")

        st.markdown("#### 📚 Available Electives Pool:")
        for course in available_electives:
            render_course_card(course, card_type="elective", locked=False)

    # Structured Output & Apply Button
    st.divider()
    st.markdown("### 📤 Output: Selected Semester & Electives")

    selected_electives_list = st.session_state[f"selected_electives_sem_{selected_sem}"]
    core_codes = [c['subject_code'] for c in sem_data['core']]
    project_codes = [c['subject_code'] for c in sem_data['project']]

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Active Semester", value=f"Semester {selected_sem}")
    with m2:
        st.metric(label="Locked Core Subjects", value=f"{len(core_codes) + len(project_codes)} Subjects")
    with m3:
        st.metric(label="Selected Electives", value=f"{', '.join(selected_electives_list) if selected_electives_list else 'None'}")

    # Synced Holidays Viewer
    holidays_dict = _sync_status.get("holidays_data", {})
    with st.expander(f"🎉 View Official IIT Patna Holiday Calendar ({len(holidays_dict)} Synced Holidays)"):
        if holidays_dict:
            cols = st.columns(2)
            sorted_items = sorted(holidays_dict.items())
            mid = (len(sorted_items) + 1) // 2
            with cols[0]:
                for d_iso, h_name in sorted_items[:mid]:
                    st.markdown(f"- 📅 **`{d_iso}`**: {h_name}")
            with cols[1]:
                for d_iso, h_name in sorted_items[mid:]:
                    st.markdown(f"- 📅 **`{d_iso}`**: {h_name}")
        else:
            st.caption("No holiday data available.")

    _, col_center_btn, _ = st.columns([1, 1.8, 1])
    with col_center_btn:
        if st.button("🚀 Apply Selection & View Academic Dashboard →", type="primary", use_container_width=True):
            user_config = {
                "semester_1": {
                    "core_courses": ["ECS 5101", "ECS 5102", "EMC 5103", "EHS 5104"],
                    "elective_1": st.session_state.get("selected_electives_sem_1", ["EAI 6103"])[0]
                },
                "semester_2": {
                    "core_courses": ["ECS 5201", "EMC 5202", "IKS"],
                    "electives": st.session_state.get("selected_electives_sem_2", ["EAI 6202", "EAI 6204"])
                },
                "semester_3": {
                    "major_project": "Project I",
                    "electives": st.session_state.get("selected_electives_sem_3", ["EAI 6301", "EAI 6302"])
                },
                "semester_4": {
                    "major_project": "Project II",
                    "electives": st.session_state.get("selected_electives_sem_4", ["EAI 6401", "EAI 6402"])
                }
            }

            with st.spinner(f"Generating Semester {selected_sem} Dashboard..."):
                main.run_curriculum_sync(
                    config=user_config,
                    target_files=[OUTPUT_HTML_PATH],
                    active_semester=selected_sem
                )

            st.session_state["dashboard_synced"] = True
            st.switch_page(dashboard_page)

    st.markdown(
        """
        <div style="text-align: center; color: var(--text-secondary); font-size: 0.88rem; padding: 2.5rem 0 1rem 0; font-weight: 500;">
            Crafted with ❤️ by <strong style="color: #000000;">Shivam Bhatt</strong> | IIT Patna (2026–2028)
        </div>
        """,
        unsafe_allow_html=True
    )


@st.cache_data(show_spinner=False)
def get_cached_dashboard_html(file_path: str, mtime: float) -> str:
    """Reads and caches the generated dashboard HTML in memory based on file modification timestamp."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# =============================================================================
# PAGE 2: ACADEMIC DASHBOARD
# =============================================================================
def page_academic_dashboard():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Auto-generate dashboard if missing (e.g., fresh cloud clone)
    if not os.path.exists(OUTPUT_HTML_PATH):
        user_config = {
            "semester_1": {
                "core_courses": ["ECS 5101", "ECS 5102", "EMC 5103", "EHS 5104"],
                "elective_1": st.session_state.get("selected_electives_sem_1", ["EAI 6103"])[0]
            },
            "semester_2": {
                "core_courses": ["ECS 5201", "EMC 5202", "IKS"],
                "electives": st.session_state.get("selected_electives_sem_2", ["EAI 6202", "EAI 6204"])
            },
            "semester_3": {
                "major_project": "Project I",
                "electives": st.session_state.get("selected_electives_sem_3", ["EAI 6301", "EAI 6302"])
            },
            "semester_4": {
                "major_project": "Project II",
                "electives": st.session_state.get("selected_electives_sem_4", ["EAI 6401", "EAI 6402"])
            }
        }
        main.run_curriculum_sync(
            config=user_config,
            target_files=[OUTPUT_HTML_PATH],
            active_semester=st.session_state.get("active_semester", 1)
        )

    # Load and Render Dashboard HTML directly using memory cache and modern st.iframe API
    if os.path.exists(OUTPUT_HTML_PATH):
        mtime = os.path.getmtime(OUTPUT_HTML_PATH)
        dashboard_html = get_cached_dashboard_html(OUTPUT_HTML_PATH, mtime)
        if dashboard_html:
            st.iframe(dashboard_html, height=1350, width="stretch")
        else:
            st.warning("⚠️ Error reading dashboard. Please regenerate curriculum.")
    else:
        st.warning("⚠️ No dashboard generated yet. Please select your curriculum first.")
        if st.button("Go to Curriculum Selector"):
            st.switch_page(selector_page)


# =============================================================================
# MULTIPAGE NAVIGATION SETUP
# =============================================================================
selector_page = st.Page(page_curriculum_selector, title="Curriculum & Electives", icon="🎓", default=True)
dashboard_page = st.Page(page_academic_dashboard, title="Academic Dashboard", icon="📊")

pg = st.navigation([selector_page, dashboard_page])
pg.run()
