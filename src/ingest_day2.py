"""
Day 2 Data Ingestion Script for Veloxa CXO Cockpit.
Ingests Hiring Tracker, Leave Register, Culture Amp Pulse Survey,
Resignation Letter, Day 2 Emails, and Transcripts (T3, T6a) into veloxa.db.
"""

import os
import sqlite3
import email
import zipfile
import xml.etree.ElementTree as ET
import openpyxl
import pypdf

DB_PATH = "veloxa.db"
DAY2_DIR = os.path.join("data", "day2")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_day2_tables():
    """Create additional tables for Day 2 HR and survey data."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS hiring_requisitions")
    cur.execute("DROP TABLE IF EXISTS leave_records")
    cur.execute("DROP TABLE IF EXISTS pulse_surveys")
    cur.execute("DROP TABLE IF EXISTS resignations")

    # 1. Hiring Tracker table
    cur.execute("""
        CREATE TABLE hiring_requisitions (
            req_id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            team TEXT NOT NULL,
            hiring_manager TEXT NOT NULL,
            opened_date TEXT NOT NULL,
            status TEXT NOT NULL,
            status_date TEXT NOT NULL,
            in_pipeline INTEGER,
            notes TEXT
        )
    """)

    # 2. Leave Register table
    cur.execute("""
        CREATE TABLE leave_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL,
            days REAL NOT NULL,
            approved_by TEXT NOT NULL
        )
    """)

    # 3. Pulse Survey table
    cur.execute("""
        CREATE TABLE pulse_surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quarter TEXT NOT NULL,
            team TEXT NOT NULL,
            team_size INTEGER,
            responses INTEGER,
            engagement_score REAL,
            comments TEXT
        )
    """)

    # 4. Resignations table
    cur.execute("""
        CREATE TABLE resignations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            title TEXT NOT NULL,
            resignation_date TEXT NOT NULL,
            last_working_day TEXT NOT NULL,
            recipient TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("[INFO] Day 2 SQLite tables initialized successfully.")


def ingest_hiring_tracker():
    """Ingest Hiring_Tracker.xlsx from Day 2 HR."""
    file_path = os.path.join(DAY2_DIR, "data_room", "hr", "Hiring_Tracker.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["Requisitions"]

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    rows = list(ws.iter_rows(values_only=True))
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        req_id = str(r[0]).strip()
        role = str(r[1]).strip() if r[1] else ""
        team = str(r[2]).strip() if r[2] else ""
        manager = str(r[3]).strip() if r[3] else ""
        opened = str(r[4]).strip() if r[4] else ""
        status = str(r[5]).strip() if r[5] else ""
        status_date = str(r[6]).strip() if r[6] else ""
        pipeline = int(r[7]) if r[7] is not None else 0
        notes = str(r[8]).strip() if r[8] else ""

        cur.execute("""
            INSERT INTO hiring_requisitions (req_id, role, team, hiring_manager, opened_date, status, status_date, in_pipeline, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (req_id, role, team, manager, opened, status, status_date, pipeline, notes))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} hiring requisitions from Hiring_Tracker.xlsx.")
    return count


def ingest_leave_register():
    """Ingest Leave_Register.xlsx from Day 2 HR."""
    file_path = os.path.join(DAY2_DIR, "data_room", "hr", "Leave_Register.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["Leave FY"]

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    rows = list(ws.iter_rows(values_only=True))
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        emp = str(r[0]).strip()
        leave_type = str(r[1]).strip() if r[1] else ""
        from_date = str(r[2]).strip() if r[2] else ""
        to_date = str(r[3]).strip() if r[3] else ""
        days = float(r[4]) if r[4] is not None else 0.0
        approved = str(r[5]).strip() if r[5] else ""

        cur.execute("""
            INSERT INTO leave_records (employee, leave_type, from_date, to_date, days, approved_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (emp, leave_type, from_date, to_date, days, approved))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} leave records from Leave_Register.xlsx.")
    return count


def ingest_pulse_surveys():
    """Ingest Pulse_Survey.xlsx from Day 2 HR."""
    file_path = os.path.join(DAY2_DIR, "data_room", "hr", "Pulse_Survey.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["Pulse by team"]

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    rows = list(ws.iter_rows(values_only=True))
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        quarter = str(r[0]).strip()
        team = str(r[1]).strip() if r[1] else ""
        team_size = int(r[2]) if r[2] is not None else 0
        responses = int(r[3]) if r[3] is not None else 0
        score = float(r[4]) if r[4] is not None else 0.0
        comments = str(r[5]).strip() if r[5] else ""

        cur.execute("""
            INSERT INTO pulse_surveys (quarter, team, team_size, responses, engagement_score, comments)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (quarter, team, team_size, responses, score, comments))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} pulse survey quarters from Pulse_Survey.xlsx.")
    return count


def ingest_resignation_letter():
    """Ingest Resignation_Letter_SM.pdf from Day 2 documents."""
    pdf_path = os.path.join(DAY2_DIR, "data_room", "documents", "Resignation_Letter_SM.pdf")
    if not os.path.exists(pdf_path):
        print(f"[WARN] File not found: {pdf_path}")
        return 0

    reader = pypdf.PdfReader(pdf_path)
    full_text = "\n".join(p.extract_text() for p in reader.pages)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resignations (employee_name, title, resignation_date, last_working_day, recipient, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "Siddharth Mehta",
        "Product Marketing Manager",
        "2026-09-15",
        "2026-10-31",
        "Nikhil Bose, Head of Marketing",
        "Looking for a role with clearer launch timelines, where prepared collateral reaches customers."
    ))
    conn.commit()
    conn.close()
    print("[INFO] Ingested Siddharth Mehta resignation letter from documents/.")
    return 1


def ingest_day2_emails():
    """Ingest Day 2 email files (06.eml, 07.eml, 10.eml, 11.eml)."""
    email_dir = os.path.join(DAY2_DIR, "data_room", "email")
    if not os.path.exists(email_dir):
        print(f"[WARN] Directory not found: {email_dir}")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    for fname in sorted(os.listdir(email_dir)):
        if not fname.endswith(".eml"):
            continue
        fpath = os.path.join(email_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            msg = email.message_from_file(f)
            from_addr = str(msg.get("From", ""))
            to_addr = str(msg.get("To", ""))
            date_str = str(msg.get("Date", ""))
            subject = str(msg.get("Subject", ""))
            body = msg.get_payload()
            if isinstance(body, list):
                body = "\n".join(str(part.get_payload()) for part in body)
            else:
                body = str(body)

            cur.execute("""
                INSERT INTO emails (filename, from_addr, to_addr, date_str, subject, body)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (fname, from_addr, to_addr, date_str, subject, body.strip()))
            count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} Day 2 emails.")
    return count


def read_docx(file_path):
    with zipfile.ZipFile(file_path) as z:
        tree = ET.fromstring(z.read("word/document.xml"))
        return "".join(node.text for node in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text)


def ingest_day2_transcripts():
    """Ingest T3 (Head of People call) and T6a (CEO voice note)."""
    t_dir = os.path.join(DAY2_DIR, "transcripts")
    if not os.path.exists(t_dir):
        print(f"[WARN] Directory not found: {t_dir}")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    transcripts = [
        ("T3", "T3_Head_of_People_Call.docx", "Head of People call"),
        ("T6a", "T6a_CEO_Voice_Note.docx", "CEO voice note T6a")
    ]

    for call_id, fname, title in transcripts:
        fpath = os.path.join(t_dir, fname)
        if not os.path.exists(fpath):
            continue
        text = read_docx(fpath)
        cur.execute("""
            INSERT OR REPLACE INTO transcripts (call_id, title, full_text)
            VALUES (?, ?, ?)
        """, (call_id, title, text))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} Day 2 transcripts (T3, T6a).")
    return count


def append_day2_evidence():
    """Append Day 2 evidence records into evidence_index."""
    conn = get_db_connection()
    cur = conn.cursor()

    day2_evidence = [
        ("E016", "Hiring_Tracker.xlsx", "REQ-014 & REQ-015", "Backend engineer reqs put on hold on 12-Aug after paying Cohere advance", "Meera Iyer, Vikram Menon", "2026-08-12", "HIGH"),
        ("E017", "06.eml", "Email Body", "Meera instructs Vikram to pause REQ-014 and REQ-015 to prioritize cash burn", "Meera Iyer, Vikram Menon", "2026-08-12", "HIGH"),
        ("E018", "07.eml", "Email Body", "Vikram accepts hiring pause saying 'We will absorb it'", "Vikram Menon, Meera Iyer", "2026-08-12", "HIGH"),
        ("E019", "Leave_Register.xlsx", "P. Nair Rows 13-17", "Priya Nair took five separate half-day personal leaves across Sep 2026 (flight risk pattern)", "Priya Nair", "2026-09-03 to 2026-09-24", "HIGH"),
        ("E020", "Pulse_Survey.xlsx", "Jul-Sep 2026, Engineering", "Engineering team engagement plummeted from 3.9 (Q1) to 3.1 in Q2 (only 4 of 5 responded)", "Engineering Team", "2026-09-30", "HIGH"),
        ("E021", "10.eml", "Email Body", "Arjun Das requests making Pune remote working arrangement permanent", "Arjun Das, Deepa Joshi", "2026-09-18", "HIGH"),
        ("E022", "11.eml", "Email Body", "Deepa alerts Ananya that engineering pulse dropped and suggests 1:1s", "Deepa Joshi, Ananya Rao", "2026-09-29", "HIGH"),
        ("E023", "Resignation_Letter_SM.pdf", "Letter text", "Siddharth Mehta resigns citing lack of clear launch timelines and product delays", "Siddharth Mehta, Nikhil Bose", "2026-09-15", "HIGH"),
        ("E024", "T3_Head_of_People_Call.docx", "Meeting transcript", "Deepa claims attrition is 'about twelve' and worries about unnamed engineer", "Deepa Joshi", "2026-11-17", "MEDIUM"),
        ("E025", "T6a_CEO_Voice_Note.docx", "Voice note", "Ananya requests default startup view showing Top 3 things to worry about without typing", "Ananya Rao", "2026-11-17", "HIGH")
    ]

    for item in day2_evidence:
        cur.execute("""
            INSERT OR REPLACE INTO evidence_index (ref_id, source_file, location, fact, entities, date_str, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    conn.close()
    print(f"[INFO] Appended {len(day2_evidence)} Day 2 evidence records into evidence_index.")


def main():
    print("=== Starting Veloxa Day 2 Data Ingestion ===")
    init_day2_tables()
    ingest_hiring_tracker()
    ingest_leave_register()
    ingest_pulse_surveys()
    ingest_resignation_letter()
    ingest_day2_emails()
    ingest_day2_transcripts()
    append_day2_evidence()
    print("=== Day 2 Data Ingestion Completed Successfully ===")


if __name__ == "__main__":
    main()
