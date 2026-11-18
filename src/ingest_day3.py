"""
Day 3 Data Ingestion Script for Veloxa CXO Cockpit.
Ingests Jira Export, PagerDuty Incidents, On-Call Rota, Git Log,
Contractor Invoices, Launch Kit, Day 3 Emails, and Transcripts (T4, T5, T6b).
"""

import os
import csv
import sqlite3
import email
import zipfile
import xml.etree.ElementTree as ET
import openpyxl
import pypdf

DB_PATH = "veloxa.db"
DAY3_DIR = os.path.join("data", "day3")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_day3_tables():
    """Create additional tables for Day 3 engineering and contractor data."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS jira_issues")
    cur.execute("DROP TABLE IF EXISTS jira_versions")
    cur.execute("DROP TABLE IF EXISTS pagerduty_incidents")
    cur.execute("DROP TABLE IF EXISTS oncall_rota")
    cur.execute("DROP TABLE IF EXISTS invoices")
    cur.execute("DROP TABLE IF EXISTS git_commits_summary")

    # 1. Jira Issues table
    cur.execute("""
        CREATE TABLE jira_issues (
            key TEXT PRIMARY KEY,
            issue_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            epic_link TEXT,
            assignee TEXT,
            story_points REAL,
            status TEXT NOT NULL,
            created_date TEXT,
            resolved_date TEXT,
            fix_version TEXT
        )
    """)

    # 2. Jira Versions table
    cur.execute("""
        CREATE TABLE jira_versions (
            version_name TEXT PRIMARY KEY,
            release_date TEXT NOT NULL,
            original_release_date TEXT NOT NULL,
            last_changed TEXT NOT NULL,
            changed_by TEXT NOT NULL
        )
    """)

    # 3. PagerDuty Incidents table
    cur.execute("""
        CREATE TABLE pagerduty_incidents (
            incident_id TEXT PRIMARY KEY,
            severity TEXT NOT NULL,
            opened_at TEXT NOT NULL,
            resolved_at TEXT NOT NULL,
            service TEXT NOT NULL,
            responder TEXT NOT NULL
        )
    """)

    # 4. OnCall Rota table
    cur.execute("""
        CREATE TABLE oncall_rota (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_of TEXT NOT NULL,
            primary_oncall TEXT NOT NULL,
            secondary_oncall TEXT NOT NULL
        )
    """)

    # 5. Invoices table
    cur.execute("""
        CREATE TABLE invoices (
            invoice_no TEXT PRIMARY KEY,
            vendor TEXT NOT NULL,
            invoice_date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL
        )
    """)

    # 6. Git Commits Summary table
    cur.execute("""
        CREATE TABLE git_commits_summary (
            author_email TEXT PRIMARY KEY,
            commit_count INTEGER NOT NULL,
            first_commit TEXT,
            last_commit TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[INFO] Day 3 SQLite tables initialized successfully.")


def ingest_jira_export():
    """Ingest Jira_Export_ATLAS.xlsx from Day 3 Engineering."""
    file_path = os.path.join(DAY3_DIR, "data_room", "engineering", "Jira_Export_ATLAS.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Ingest Versions
    ws_v = wb["Versions"]
    v_rows = list(ws_v.iter_rows(values_only=True))
    for r in v_rows[1:]:
        if not r or not r[0]:
            continue
        v_name = str(r[0]).strip()
        rel_date = str(r[1]).strip() if r[1] else ""
        orig_rel_date = str(r[2]).strip() if r[2] else ""
        last_changed = str(r[3]).strip() if r[3] else ""
        changed_by = str(r[4]).strip() if r[4] else ""
        cur.execute("""
            INSERT OR REPLACE INTO jira_versions (version_name, release_date, original_release_date, last_changed, changed_by)
            VALUES (?, ?, ?, ?, ?)
        """, (v_name, rel_date, orig_rel_date, last_changed, changed_by))

    # 2. Ingest Issues
    ws_i = wb["Issues"]
    i_rows = list(ws_i.iter_rows(values_only=True))
    count = 0
    for r in i_rows[3:]:
        if not r or not r[0]:
            continue
        key = str(r[0]).strip()
        issue_type = str(r[1]).strip() if r[1] else "Story"
        summary = str(r[2]).strip() if r[2] else ""
        epic = str(r[3]).strip() if r[3] else ""
        assignee = str(r[4]).strip() if r[4] else ""
        pts = float(r[5]) if r[5] is not None else 0.0
        status = str(r[6]).strip() if r[6] else "To Do"
        created = str(r[7]).strip() if r[7] else ""
        resolved = str(r[8]).strip() if r[8] else None
        fix_v = str(r[9]).strip() if r[9] else ""

        cur.execute("""
            INSERT OR REPLACE INTO jira_issues (key, issue_type, summary, epic_link, assignee, story_points, status, created_date, resolved_date, fix_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (key, issue_type, summary, epic, assignee, pts, status, created, resolved, fix_v))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} Jira issues and 1 version from Jira_Export_ATLAS.xlsx.")
    return count


def ingest_incidents():
    """Ingest Incidents_Aug-Oct_2026.xlsx from Day 3 Engineering."""
    file_path = os.path.join(DAY3_DIR, "data_room", "engineering", "Incidents_Aug-Oct_2026.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["Incidents"]

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    rows = list(ws.iter_rows(values_only=True))
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        inc_id = str(r[0]).strip()
        sev = str(r[1]).strip() if r[1] else ""
        opened = str(r[2]).strip() if r[2] else ""
        resolved = str(r[3]).strip() if r[3] else ""
        service = str(r[4]).strip() if r[4] else ""
        responder = str(r[5]).strip() if r[5] else ""

        cur.execute("""
            INSERT OR REPLACE INTO pagerduty_incidents (incident_id, severity, opened_at, resolved_at, service, responder)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (inc_id, sev, opened, resolved, service, responder))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} PagerDuty incidents from Incidents_Aug-Oct_2026.xlsx.")
    return count


def ingest_oncall_rota():
    """Ingest OnCall_Rota.xlsx from Day 3 Engineering."""
    file_path = os.path.join(DAY3_DIR, "data_room", "engineering", "OnCall_Rota.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["On-call"]

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    rows = list(ws.iter_rows(values_only=True))
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        week = str(r[0]).strip()
        prim = str(r[1]).strip() if r[1] else ""
        sec = str(r[2]).strip() if r[2] else ""

        cur.execute("""
            INSERT INTO oncall_rota (week_of, primary_oncall, secondary_oncall)
            VALUES (?, ?, ?)
        """, (week, prim, sec))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} weeks of on-call rota from OnCall_Rota.xlsx.")
    return count


def ingest_git_log():
    """Ingest and summarize git_log.csv."""
    file_path = os.path.join(DAY3_DIR, "data_room", "engineering", "git_log.csv")
    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        return 0

    author_stats = {}
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email_addr = row["author_email"].strip().lower()
            date = row["committed_at"].strip()
            if email_addr not in author_stats:
                author_stats[email_addr] = {
                    "count": 0,
                    "first": date,
                    "last": date
                }
            author_stats[email_addr]["count"] += 1
            if date < author_stats[email_addr]["first"]:
                author_stats[email_addr]["first"] = date
            if date > author_stats[email_addr]["last"]:
                author_stats[email_addr]["last"] = date

    conn = get_db_connection()
    cur = conn.cursor()
    for email_addr, stats in author_stats.items():
        cur.execute("""
            INSERT OR REPLACE INTO git_commits_summary (author_email, commit_count, first_commit, last_commit)
            VALUES (?, ?, ?, ?)
        """, (email_addr, stats["count"], stats["first"], stats["last"]))

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested git commit activity for {len(author_stats)} authors from git_log.csv.")
    return len(author_stats)


def ingest_invoice():
    """Ingest Invoice_PIS-114.pdf from Day 3 documents."""
    pdf_path = os.path.join(DAY3_DIR, "data_room", "documents", "Invoice_PIS-114.pdf")
    if not os.path.exists(pdf_path):
        print(f"[WARN] File not found: {pdf_path}")
        return 0

    reader = pypdf.PdfReader(pdf_path)
    full_text = "\n".join(p.extract_text() for p in reader.pages)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO invoices (invoice_no, vendor, invoice_date, amount, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "PIS-114",
        "Patil Infra Services",
        "2026-10-01",
        141600.0,
        "On-call SRE support, S. Patil, September 2026 (monthly retainer, Rs. 1,20,000 + 18% IGST)"
    ))
    conn.commit()
    conn.close()
    print("[INFO] Ingested Patil Infra Services invoice PIS-114 (Rs. 1,41,600).")
    return 1


def ingest_day3_emails():
    """Ingest Day 3 emails (04.eml, 05.eml, 08.eml, 09.eml)."""
    email_dir = os.path.join(DAY3_DIR, "data_room", "email")
    if not os.path.exists(email_dir):
        print(f"[WARN] Directory not found: {email_dir}")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    for fname in ["04.eml", "05.eml", "08.eml", "09.eml"]:
        fpath = os.path.join(email_dir, fname)
        if not os.path.exists(fpath):
            continue
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
    print(f"[INFO] Ingested {count} Day 3 emails.")
    return count


def read_docx(file_path):
    with zipfile.ZipFile(file_path) as z:
        tree = ET.fromstring(z.read("word/document.xml"))
        return "".join(node.text for node in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text)


def ingest_day3_transcripts():
    """Ingest T4, T5, and T6b."""
    t_dir = os.path.join(DAY3_DIR, "transcripts")
    if not os.path.exists(t_dir):
        print(f"[WARN] Directory not found: {t_dir}")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    transcripts = [
        ("T4", "T4_Head_of_Marketing_Call.docx", "Head of Marketing call"),
        ("T5", "T5_VP_Engineering_Call.docx", "VP Engineering call"),
        ("T6b", "T6b_CEO_Voice_Note.docx", "CEO voice note T6b")
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
    print(f"[INFO] Ingested {count} Day 3 transcripts (T4, T5, T6b).")
    return count


def append_day3_evidence():
    """Append Day 3 evidence records into evidence_index."""
    conn = get_db_connection()
    cur = conn.cursor()

    day3_evidence = [
        ("E026", "Jira_Export_ATLAS.xlsx", "Sheet: Versions, Row 2", "Atlas GA release date was postponed by Vikram from 2026-09-15 to 2026-12-15 on 2026-09-02", "Vikram Menon, Atlas GA", "2026-09-02", "HIGH"),
        ("E027", "T5_VP_Engineering_Call.docx", "Meeting transcript", "Vikram tells Ananya v3 is 'on track, maybe a couple weeks buffer, September-ish' while Jira shows 15-Dec", "Vikram Menon, Ananya Rao", "2026-11-18", "LOW"),
        ("E028", "Incidents_Aug-Oct_2026.xlsx", "Incidents: INC-201, INC-203, INC-205", "Three SEV1 outages on routing-api in August 2026 handled by Sneha Kulkarni", "Sneha Kulkarni", "2026-08-04 to 2026-08-23", "HIGH"),
        ("E029", "08.eml", "Email Body", "Sneha notifies Vikram of 3rd SEV1, pauses Atlas perf tickets, brings contractor on rota", "Sneha Kulkarni, Vikram Menon", "2026-08-24", "HIGH"),
        ("E030", "OnCall_Rota.xlsx", "On-call sheet", "Sneha listed as both Primary and Secondary ('Snehal') on-call continuously from August to October", "Sneha Kulkarni", "2026-08-17 to 2026-10-26", "HIGH"),
        ("E031", "Invoice_PIS-114.pdf", "Invoice text", "Patil Infra Services billed Rs. 1,41,600 (Rs. 1,20,000 + IGST) for full-month September on-call SRE support", "Patil Infra Services", "2026-10-01", "HIGH"),
        ("E032", "09.eml", "Email Body", "Priya sends late-night email (23:47) asking to talk about Atlas ownership", "Priya Nair, Vikram Menon", "2026-09-01", "HIGH"),
        ("E033", "Atlas_Launch_Kit_v1.pdf", "Document text", "Siddharth completed Atlas launch deck, website page, and email sequence on 21 Jul 2026", "Siddharth Mehta", "2026-07-21", "HIGH"),
        ("E034", "05.eml", "Email Body", "Siddharth informs Nikhil that launch kit is done and just waiting for engineering date", "Siddharth Mehta, Nikhil Bose", "2026-07-22", "HIGH"),
        ("E035", "T4_Head_of_Marketing_Call.docx", "Meeting transcript", "Nikhil states Sid launch kit ready since July; Manoj claims summit leads are cold", "Nikhil Bose, Manoj Kumar", "2026-11-18", "MEDIUM"),
        ("E036", "T6b_CEO_Voice_Note.docx", "Voice note", "Ananya says marketing will report to new CRO from next month or month after", "Ananya Rao", "2026-11-18", "HIGH")
    ]

    for item in day3_evidence:
        cur.execute("""
            INSERT OR REPLACE INTO evidence_index (ref_id, source_file, location, fact, entities, date_str, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    conn.close()
    print(f"[INFO] Appended {len(day3_evidence)} Day 3 evidence records into evidence_index.")


def main():
    print("=== Starting Veloxa Day 3 Data Ingestion ===")
    init_day3_tables()
    ingest_jira_export()
    ingest_incidents()
    ingest_oncall_rota()
    ingest_git_log()
    ingest_invoice()
    ingest_day3_emails()
    ingest_day3_transcripts()
    append_day3_evidence()
    print("=== Day 3 Data Ingestion Completed Successfully ===")


if __name__ == "__main__":
    main()
