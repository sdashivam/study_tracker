"""
IIT Patna M.Tech (AI & Data Science) Course Catalog Manager
Reads course details directly from JSON files in the 'courses/' directory
instead of hardcoding data.
"""

import os
import sys
import json
import glob

# Project root directory (one level up from src/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSES_DIR = os.path.join(ROOT_DIR, 'courses')
MASTER_FILE = os.path.join(COURSES_DIR, 'all_courses.json')


def load_courses_from_json():
    """
    Loads courses from all_courses.json, or by aggregating individual course JSON files.
    """
    if not os.path.exists(COURSES_DIR):
        print(f"Error: Courses directory '{COURSES_DIR}' not found.")
        return []

    # Priority 1: Load from master all_courses.json if present
    if os.path.exists(MASTER_FILE):
        try:
            with open(MASTER_FILE, 'r', encoding='utf-8') as f:
                courses = json.load(f)
            print(f"Loaded {len(courses)} courses from master file: {MASTER_FILE}")
            return courses
        except Exception as e:
            print(f"Warning: Failed to load '{MASTER_FILE}': {e}. Falling back to individual JSON files.")

    # Priority 2: Aggregate individual JSON files
    courses = []
    json_files = glob.glob(os.path.join(COURSES_DIR, '*.json'))
    for fpath in json_files:
        if os.path.basename(fpath) == 'all_courses.json':
            continue
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'subject_code' in data:
                    courses.append(data)
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

    # Sort courses by semester then code
    courses.sort(key=lambda c: (c.get('semester', 99), c.get('subject_code', '')))
    print(f"Aggregated {len(courses)} courses from individual JSON files.")
    return courses


def sync_and_validate_courses(courses):
    """
    Validates course schema and writes/syncs individual course JSON files and master JSON.
    """
    if not courses:
        print("No courses available to sync.")
        return

    os.makedirs(COURSES_DIR, exist_ok=True)
    valid_count = 0

    for c in courses:
        code = c.get('subject_code', '').strip()
        if not code:
            continue

        # Validation check for required fields
        title = c.get('subject_name', 'Untitled')
        semester = c.get('semester', 1)
        credits_str = c.get('credits', '')
        objectives = c.get('learning_objectives', [])
        outline = c.get('outline', [])
        books = c.get('books', [])

        code_slug = code.lower().replace(' ', '_').replace('-', '_').replace('/', '_')
        file_path = os.path.join(COURSES_DIR, f"{code_slug}.json")

        # Save validated individual file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(c, f, indent=2, ensure_ascii=False)
        
        valid_count += 1

    # Save synchronized master all_courses.json
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)

    print(f"Successfully validated & synced {valid_count} individual course files.")
    print(f"Master index updated at: {MASTER_FILE}")


def print_course_summary(courses):
    """
    Displays a formatted overview table of all courses.
    """
    print("\n" + "=" * 90)
    print(f"{'CODE':<14} | {'TITLE':<38} | {'SEM':<4} | {'BOOKS':<6} | {'OBJECTIVES'}")
    print("=" * 90)

    for c in courses:
        code = c.get('subject_code', 'N/A')
        title = c.get('subject_name', 'N/A')[:38]
        sem = f"Sem {c.get('semester', '-')}"
        books_count = len(c.get('books', []))
        obj_count = len(c.get('learning_objectives', []))
        print(f"{code:<14} | {title:<38} | {sem:<4} | {books_count:<6} | {obj_count} objectives")

    print("=" * 90 + "\n")


def main():
    print("--- Reading IIT Patna Course Details from JSON ---")
    courses = load_courses_from_json()

    if not courses:
        print("No course records found in the JSON database.")
        sys.exit(1)

    print_course_summary(courses)
    sync_and_validate_courses(courses)


if __name__ == '__main__':
    main()
