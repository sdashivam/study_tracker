#!/usr/bin/env python3
"""
=============================================================================
IIT Patna M.Tech (AI & Data Science) — Timetable & Electives Synchronizer
=============================================================================
Reads:
  1. Classes/timetable_web.html (Official CETPG HTML Timetable Grid)
  2. courses/all_courses.json   (Master 24-Course Catalog with Books & Outlines)
  3. User Elective Preferences (Semester-wise selected electives)

Updates:
  - output/index.html & index.html (Embedded timetable slots, course analytics, and overview cards)
=============================================================================
"""

import os
import sys
import re
import json
import shutil
import argparse
from bs4 import BeautifulSoup

# Project root directory (one level up from src/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TIMETABLE = os.path.join(ROOT_DIR, 'Classes', 'timetable_web.html')
DEFAULT_COURSES = os.path.join(ROOT_DIR, 'courses', 'all_courses.json')
DEFAULT_INDEX = os.path.join(ROOT_DIR, 'index.html')
DEFAULT_OUTPUT_INDEX = os.path.join(ROOT_DIR, 'output', 'index.html')
DEFAULT_PORTAL_URL = "https://cetpgex.iitp.ac.in/index.php/academics/time-table?view=article&id=39&catid=2"


def fetch_live_timetable(url=None, target_file=DEFAULT_TIMETABLE, timeout=6):
    """
    On-Demand Sync: Fetches the latest official timetable HTML from the live IIT Patna portal.
    If successful, overwrites target_file on disk.
    If offline or unreachable, gracefully falls back to the existing cached file.
    """
    source_url = url or os.getenv("IITP_TIMETABLE_URL") or DEFAULT_PORTAL_URL
    try:
        import urllib.request
        req = urllib.request.Request(source_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                html_content = response.read().decode('utf-8', errors='replace')
                if '<table' in html_content:
                    os.makedirs(os.path.dirname(os.path.abspath(target_file)), exist_ok=True)
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    return True, f"Live timetable synced from IIT Patna portal ({source_url})"
    except Exception as e:
        return False, f"Could not reach live portal ({e}). Using cached local timetable."
    return False, "Using cached local timetable."


DEFAULT_HOLIDAYS = os.path.join(ROOT_DIR, 'courses', 'holidays.json')
DEFAULT_HOLIDAYS_BASE_URL = "https://cetpgex.iitp.ac.in/index.php/academics/institute-holidays-for-the-year-"


def clean_holiday_name(name):
    """Sanitizes holiday names and removes unicode encoding artifacts."""
    name = re.sub(r'[\ufffd\x80-\xff]+', "'", str(name))
    name = name.replace("’", "'").replace("`", "'").replace("*", "").strip()
    return name


def fetch_live_holidays(target_file=DEFAULT_HOLIDAYS, timeout=6):
    """
    On-Demand & Automatic End-of-Year Sync:
    Fetches the official IIT Patna Holiday Calendar directly from CETPG portal.
    Automatically determines current & upcoming academic years at year-end,
    parses HTML table into standard YYYY-MM-DD format, and updates courses/holidays.json.
    """
    import datetime
    import urllib.request

    now = datetime.datetime.now()
    # At the end of the year (Nov/Dec), auto-check both current and upcoming year for seamless rollover
    target_years = [now.year]
    if now.month in [11, 12]:
        target_years.append(now.year + 1)
    elif now.month == 1:
        target_years.append(now.year - 1)
    for y in [2025, 2026, 2027]:
        if y not in target_years:
            target_years.append(y)

    merged_holidays = {}

    # Load existing cached holidays if present
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                if isinstance(cached_data, dict) and "holidays" in cached_data:
                    merged_holidays.update(cached_data["holidays"])
                elif isinstance(cached_data, dict):
                    merged_holidays.update(cached_data)
        except Exception:
            pass

    urls_to_try = [
        "https://cetpgex.iitp.ac.in/index.php/academics/institute-holidays-for-the-year-2025"
    ]
    for yr in target_years:
        urls_to_try.append(f"{DEFAULT_HOLIDAYS_BASE_URL}{yr}")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    newly_synced = 0

    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    html_content = response.read().decode('utf-8', errors='replace')
                    soup = BeautifulSoup(html_content, 'html.parser')
                    table = soup.find('table')
                    if table:
                        for row in table.find_all('tr'):
                            cols = [c.get_text().strip() for c in row.find_all(['td', 'th'])]
                            if len(cols) >= 3:
                                raw_name = clean_holiday_name(cols[1])
                                date_str = cols[2]
                                d_match = re.search(r'(\d{1,2})[\.\/-](\d{1,2})[\.\/-](\d{4})', date_str)
                                if d_match:
                                    d, m, y = d_match.groups()
                                    iso = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
                                    if raw_name and raw_name.lower() not in ["holiday", "sl. no.", "name"]:
                                        merged_holidays[iso] = raw_name
                                        newly_synced += 1
        except Exception:
            continue

    # Default fallback baseline holidays if live fetch had zero
    if not merged_holidays:
        merged_holidays = {
            "2026-08-15": "Independence Day",
            "2026-08-26": "Prophet Mohammad's Birthday (Id-E-Milad)",
            "2026-10-02": "Mahatma Gandhi's Birthday",
            "2026-10-19": "Dussehra (Mahasthami)",
            "2026-10-20": "Dussehra (Mahanavmi) / Vijay Dashmi",
            "2026-11-08": "Diwali (Deepavali)",
            "2026-11-16": "Chhath Puja",
            "2026-11-24": "Guru Nanak's Birthday",
            "2026-12-25": "Christmas Day"
        }

    try:
        os.makedirs(os.path.dirname(os.path.abspath(target_file)), exist_ok=True)
        payload = {
            "last_synced": datetime.datetime.now().isoformat(),
            "academic_years_covered": target_years,
            "total_holidays": len(merged_holidays),
            "holidays": merged_holidays
        }
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        return True, f"Live holiday calendar synced ({len(merged_holidays)} holidays registered)", merged_holidays
    except Exception as e:
        return False, f"Using local holidays ({e})", merged_holidays


def convert_to_24h(time_str):
    """Converts 12-hour time string (e.g. '8:00 AM', '12:30 PM') to 24-hour '08:00'."""
    time_str = time_str.strip()
    match = re.match(r'(\d+):(\d+)\s*(AM|PM)', time_str, re.IGNORECASE)
    if not match:
        return time_str
    h, m, mod = match.groups()
    h, m = int(h), int(m)
    if mod.upper() == 'PM' and h < 12:
        h += 12
    if mod.upper() == 'AM' and h == 12:
        h = 0
    return f"{h:02d}:{m:02d}"


def format_12h(time_24h):
    """Converts '08:00' to '8:00 AM'."""
    h, m = map(int, time_24h.split(':'))
    mod = 'AM' if h < 12 else 'PM'
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12}:{m:02d} {mod}"


def merge_intervals_to_slots(intervals):
    """
    Merges adjacent 30-minute grid cells into continuous lecture slots.
    Input intervals: [{'day': 6, 'timeSlot': '8:00 AM – 8:30 AM'}, ...]
    Output: [{'day': 6, 'start': '08:00', 'end': '09:30', 'label': '8:00 AM – 9:30 AM'}, ...]
    """
    by_day = {}
    for item in intervals:
        d = item['day']
        if d not in by_day:
            by_day[d] = []
        raw = item['timeSlot'].replace('–', '-').replace('—', '-').split('-')
        if len(raw) == 2:
            s24 = convert_to_24h(raw[0].strip())
            e24 = convert_to_24h(raw[1].strip())
            by_day[d].append((s24, e24))

    merged = []
    for d, times in sorted(by_day.items()):
        if not times:
            continue
        times.sort()
        curr_s, curr_e = times[0]
        for n_s, n_e in times[1:]:
            if n_s == curr_e:
                curr_e = n_e
            elif n_s > curr_e:
                merged.append({
                    'day': d,
                    'start': curr_s,
                    'end': curr_e,
                    'label': f"{format_12h(curr_s)} – {format_12h(curr_e)}"
                })
                curr_s, curr_e = n_s, n_e
        merged.append({
            'day': d,
            'start': curr_s,
            'end': curr_e,
            'label': f"{format_12h(curr_s)} – {format_12h(curr_e)}"
        })

    return merged


def parse_timetable_html(file_path):
    """
    Parses timetable_web.html and extracts courses, faculties, and raw time slots.
    """
    if not os.path.exists(file_path):
        print(f"Error: Timetable file not found at: {file_path}")
        return {}

    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    table = soup.find('table')
    if not table:
        print("Error: No timetable table found in HTML.")
        return {}

    rows = table.find_all('tr')
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday', 'Sunday']
    day_to_num = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}

    courses_dict = {}

    for r in rows:
        tds = r.find_all('td')
        if not tds:
            continue
        time_slot = tds[0].get_text().strip()
        if not time_slot or ('–' not in time_slot and '-' not in time_slot):
            continue

        for idx, td in enumerate(tds[1:]):
            if idx >= len(day_names):
                continue
            day = day_names[idx]
            day_num = day_to_num.get(day, 0)

            # Find all card divs inside table cell
            card_divs = []
            for div in td.find_all('div'):
                div_text = div.get_text().strip()
                if any(k in div_text for k in ['ECS', 'EMC', 'EHS', 'EAI', 'EAS', 'ECC', 'ESD', 'MCA']):
                    if any(t in div_text for t in ['Dr.', 'Mr.', 'Prof.', 'CORE', 'ELECTIVE']):
                        card_divs.append(div)

            if not card_divs:
                for div in td.find_all('div', recursive=False):
                    if div.get_text().strip():
                        card_divs.append(div)

            for card in card_divs:
                lines = [l.strip() for l in card.get_text('\n').splitlines() if l.strip()]
                if not lines:
                    continue

                code = lines[0]
                if not any(c in code for c in ['ECS', 'EMC', 'EHS', 'EAI', 'EAS', 'ECC', 'ESD', 'MCA']):
                    continue

                name = lines[1] if len(lines) > 1 else ''
                credits_line = lines[2] if len(lines) > 2 else ''
                faculty = lines[3] if len(lines) > 3 else ''

                # Normalize key
                key = code.split('/')[0].strip()

                if key not in courses_dict:
                    courses_dict[key] = {
                        'full_code': code,
                        'name': name,
                        'credits': credits_line.replace('[CORE]', '').replace('[ELECTIVE]', '').strip(),
                        'faculty': faculty.replace('👤', '').strip(),
                        'is_core': 'CORE' in credits_line or 'ECS' in key or 'EMC' in key or 'EHS' in key,
                        'raw_intervals': []
                    }

                courses_dict[key]['raw_intervals'].append({
                    'day': day_num,
                    'dayName': day,
                    'timeSlot': time_slot
                })

    # Process and merge slots for each course
    for key, data in courses_dict.items():
        data['slots'] = merge_intervals_to_slots(data['raw_intervals'])

    return courses_dict


def load_courses_catalog(courses_file):
    """Loads all 24 courses from all_courses.json."""
    if not os.path.exists(courses_file):
        print(f"Error: Course catalog file '{courses_file}' not found.")
        return []

    with open(courses_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_course_in_catalog(code_query, catalog):
    """Finds matching course object in master catalog."""
    normalized_q = code_query.lower().replace('/', '').replace('-', '').replace(' ', '')
    for c in catalog:
        c_code = c.get('subject_code', '').lower().replace('/', '').replace('-', '').replace(' ', '')
        if normalized_q == c_code or normalized_q in c_code or c_code in normalized_q:
            return c
    return None


def generate_user_sem1_courses_js(timetable_data, sem1_elective_code, catalog):
    """
    Builds the USER_SEM1_COURSES JavaScript array with exact merged slots for Sem 1.
    4 Core courses + 1 chosen elective.
    """
    sem1_core_keys = ['ECS 5101', 'ECS 5102', 'EMC 5103', 'EHS 5104']
    selected_keys = sem1_core_keys + [sem1_elective_code]

    js_courses = []

    for key in selected_keys:
        # Match with timetable
        tt_match = None
        for tt_k, tt_v in timetable_data.items():
            if key.lower().replace(' ', '') in tt_k.lower().replace(' ', ''):
                tt_match = tt_v
                break

        # Match with catalog
        cat_match = find_course_in_catalog(key, catalog)

        code_val = tt_match['full_code'] if tt_match else (cat_match['subject_code'] if cat_match else key)
        name_val = cat_match['subject_name'] if cat_match else (tt_match['name'] if tt_match else key)
        type_val = "CORE" if key in sem1_core_keys else "ELECTIVE"
        credits_val = tt_match['credits'] if tt_match and tt_match['credits'] else (cat_match['credits'] if cat_match else "L3-T0-P0 | 3 Cr")
        faculty_val = tt_match['faculty'] if tt_match and tt_match['faculty'] else "IIT Patna Faculty"
        color_val = "#3b82f6" if type_val == "CORE" else "#f59e0b"
        slots_val = tt_match['slots'] if tt_match else []

        js_courses.append({
            "code": code_val,
            "name": name_val,
            "type": type_val,
            "credits": credits_val,
            "faculty": faculty_val,
            "color": color_val,
            "slots": slots_val
        })

    return js_courses


def update_index_html(index_file, user_sem1_courses, all_courses_data, elective_selections=None):
    """
    Updates target index.html (e.g. output/index.html) with fresh timetable slots and master course data.
    """
    # Ensure parent output directory exists
    out_dir = os.path.dirname(os.path.abspath(index_file))
    os.makedirs(out_dir, exist_ok=True)

    # If target file doesn't exist, copy from candidate template
    if not os.path.exists(index_file):
        for candidate in [DEFAULT_OUTPUT_INDEX, DEFAULT_INDEX]:
            if os.path.exists(candidate):
                shutil.copy(candidate, index_file)
                break
        if not os.path.exists(index_file):
            print(f"Error: No source HTML template found to initialize {index_file}.")
            return False

    with open(index_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update USER_SEM1_COURSES JS constant
    sem1_courses_json = json.dumps(user_sem1_courses, indent=6, ensure_ascii=False)
    user_courses_pattern = r'(const\s+USER_SEM1_COURSES\s*=\s*)\[[\s\S]*?\];'
    replacement = f"const USER_SEM1_COURSES = {sem1_courses_json};"
    html = re.sub(user_courses_pattern, replacement, html, count=1)

    # 2. Update ALL_COURSES_DATA JS constant
    all_courses_json = json.dumps(all_courses_data, indent=2, ensure_ascii=False)
    all_courses_pattern = r'(const\s+ALL_COURSES_DATA\s*=\s*)\[[\s\S]*?\];'
    replacement_all = f"const ALL_COURSES_DATA = {all_courses_json};"
    html = re.sub(all_courses_pattern, replacement_all, html, count=1)

    # Write back updated HTML
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Sync IIT Patna timetable_web.html and courses catalog into index.html."
    )
    parser.add_argument('--timetable', default=DEFAULT_TIMETABLE, help="Path to Classes/timetable_web.html")
    parser.add_argument('--courses', default=DEFAULT_COURSES, help="Path to courses/all_courses.json")
    parser.add_argument('--index', default=DEFAULT_OUTPUT_INDEX, help="Path to output/index.html")
    parser.add_argument('--sem1-elective', default="EAI 6103", help="Elective I course code (default: EAI 6103)")
    parser.add_argument('--sem2-electives', default="EAI 6202, EAI 6204", help="Elective II & III codes")
    parser.add_argument('--sem3-electives', default="EAI 6301, EAI 6302", help="Elective IV & V codes")
    parser.add_argument('--sem4-electives', default="EAI 6401, EAI 6402", help="Elective VI & VII codes")
    parser.add_argument('--list-electives', action='store_true', help="List all available electives and exit")

    args = parser.parse_args()

    print("=" * 80)
    print("IIT Patna M.Tech - Timetable & Electives Synchronizer")
    print("=" * 80)

    # 1. Parse Timetable
    print(f"\n[1/4] Parsing timetable grid from: {args.timetable}")
    timetable_data = parse_timetable_html(args.timetable)
    print(f"      -> Successfully extracted {len(timetable_data)} courses with timetable lecture slots.")

    if args.list_electives:
        print("\nAvailable Electives in Timetable:")
        for k, v in timetable_data.items():
            if not v['is_core']:
                print(f"  * {k:<12} : {v['name']} ({v['faculty']}) - {len(v['slots'])} weekly slots")
        return

    # 2. Load Master Course Catalog
    print(f"\n[2/4] Loading master course catalog from: {args.courses}")
    catalog = load_courses_catalog(args.courses)
    print(f"      -> Successfully loaded {len(catalog)} courses.")

    # 3. Build Synchronized Semester 1 Schedule
    print(f"\n[3/4] Configuring Semester 1 with Elective: {args.sem1_elective}")
    sem1_courses = generate_user_sem1_courses_js(timetable_data, args.sem1_elective, catalog)

    total_slots = sum(len(c['slots']) for c in sem1_courses)
    print(f"      -> Enrolled in 4 Core + 1 Elective ({len(sem1_courses)} courses, {total_slots} weekly sessions).")
    for c in sem1_courses:
        print(f"         - [{c['type']}] {c['code']} | {c['name']} (Faculty: {c['faculty']}) -> {len(c['slots'])} slots")

    # 4. Update index.html in output/ and root
    print(f"\n[4/4] Synchronizing into web dashboard: {args.index}")
    success_out = update_index_html(args.index, sem1_courses, catalog, {
        'sem1': args.sem1_elective,
        'sem2': args.sem2_electives,
        'sem3': args.sem3_electives,
        'sem4': args.sem4_electives
    })

    # Also sync root index.html
    update_index_html(DEFAULT_INDEX, sem1_courses, catalog)

    if success_out:
        print(f"      -> [SUCCESS] Generated and updated {args.index} successfully!")
    else:
        print("      -> [FAILED] Could not update index.html.")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
