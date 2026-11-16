"""
Day 1 Data Ingestion Script for Veloxa CXO Cockpit.
Ingests HRMS, Payroll, General Ledger, Emails, Board Updates, and Call Transcripts
into a local SQLite database (veloxa.db) and builds an evidence index.
"""

import os
import re
import sqlite3
import json
import email
import zipfile
import xml.etree.ElementTree as ET
import openpyxl
import pypdf

DB_PATH = "veloxa.db"
DAY1_DIR = os.path.join("data", "day1")


def get_db_connection():
    """Create or connect to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database tables for Day 1."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Drop existing tables to allow clean re-runs
    cur.execute("DROP TABLE IF EXISTS employees")
    cur.execute("DROP TABLE IF EXISTS payroll_records")
    cur.execute("DROP TABLE IF EXISTS general_ledger")
    cur.execute("DROP TABLE IF EXISTS emails")
    cur.execute("DROP TABLE IF EXISTS board_updates")
    cur.execute("DROP TABLE IF EXISTS transcripts")
    cur.execute("DROP TABLE IF EXISTS evidence_index")

    # 1. Employees table
    cur.execute("""
        CREATE TABLE employees (
            emp_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            work_email TEXT NOT NULL,
            department TEXT NOT NULL,
            title TEXT NOT NULL,
            manager_id TEXT,
            join_date TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL,
            exit_date TEXT
        )
    """)

    # 2. Payroll table
    cur.execute("""
        CREATE TABLE payroll_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            name TEXT NOT NULL,
            month TEXT NOT NULL,
            days_in_month INTEGER,
            days_payable INTEGER,
            gross REAL,
            deductions REAL,
            net REAL,
            processed_by TEXT
        )
    """)

    # 3. General Ledger table
    cur.execute("""
        CREATE TABLE general_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            txn_date TEXT NOT NULL,
            voucher TEXT NOT NULL,
            vendor TEXT NOT NULL,
            ref TEXT,
            cost_centre TEXT NOT NULL,
            amount REAL NOT NULL,
            narration TEXT,
            entered_by TEXT
        )
    """)

    # 4. Emails table
    cur.execute("""
        CREATE TABLE emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            from_addr TEXT NOT NULL,
            to_addr TEXT NOT NULL,
            date_str TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL
        )
    """)

    # 5. Board updates table
    cur.execute("""
        CREATE TABLE board_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            period TEXT NOT NULL,
            sent_date TEXT NOT NULL,
            arr TEXT,
            customers INTEGER,
            team_size INTEGER,
            monthly_burn TEXT,
            runway TEXT,
            full_text TEXT
        )
    """)

    # 6. Transcripts table
    cur.execute("""
        CREATE TABLE transcripts (
            call_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            key_points TEXT,
            action_items TEXT,
            full_text TEXT
        )
    """)

    # 7. Evidence index table for quick citation
    cur.execute("""
        CREATE TABLE evidence_index (
            ref_id TEXT PRIMARY KEY,
            source_file TEXT NOT NULL,
            location TEXT NOT NULL,
            fact TEXT NOT NULL,
            entities TEXT,
            date_str TEXT,
            confidence TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("[INFO] SQLite tables created successfully.")


def ingest_employees():
    """Ingest Employee_Master.xlsx from Day 1 HR."""
    file_path = os.path.join(DAY1_DIR, "data_room", "hr", "Employee_Master.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] Employee file not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["Employees"]

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    # Headers start at row 3 (0-indexed 2)
    rows = list(ws.iter_rows(values_only=True))
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        emp_id = str(r[0]).strip()
        full_name = str(r[1]).strip() if r[1] else ""
        work_email = str(r[2]).strip() if r[2] else ""
        dept = str(r[3]).strip() if r[3] else ""
        title = str(r[4]).strip() if r[4] else ""
        manager_id = str(r[5]).strip() if r[5] else None
        join_date = str(r[6]).strip() if r[6] else ""
        location = str(r[7]).strip() if r[7] else ""
        status = str(r[8]).strip() if r[8] else "Active"
        exit_date = str(r[9]).strip() if r[9] else None

        cur.execute("""
            INSERT INTO employees (emp_id, full_name, work_email, department, title, manager_id, join_date, location, status, exit_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (emp_id, full_name, work_email, dept, title, manager_id, join_date, location, status, exit_date))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} employees from Employee_Master.xlsx.")
    return count


def ingest_payroll():
    """Ingest Payroll_Register_Jan-Mar_2026.xlsx from Day 1 Finance."""
    file_path = os.path.join(DAY1_DIR, "data_room", "finance", "Payroll_Register_Jan-Mar_2026.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] Payroll file not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["Payroll Q4"]

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    rows = list(ws.iter_rows(values_only=True))
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        emp_id = str(r[0]).strip()
        name = str(r[1]).strip() if r[1] else ""
        month = str(r[2]).strip() if r[2] else ""
        days_in_month = int(r[3]) if r[3] is not None else 0
        days_payable = int(r[4]) if r[4] is not None else 0
        gross = float(r[5]) if r[5] is not None else 0.0
        deductions = float(r[6]) if r[6] is not None else 0.0
        net = float(r[7]) if r[7] is not None else 0.0
        processed_by = str(r[8]).strip() if r[8] else ""

        cur.execute("""
            INSERT INTO payroll_records (emp_id, name, month, days_in_month, days_payable, gross, deductions, net, processed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (emp_id, name, month, days_in_month, days_payable, gross, deductions, net, processed_by))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} payroll records from Payroll_Register_Jan-Mar_2026.xlsx.")
    return count


def ingest_general_ledger():
    """Ingest GL_Export_Apr-Sep_2026.xlsx from Day 1 Finance."""
    file_path = os.path.join(DAY1_DIR, "data_room", "finance", "GL_Export_Apr-Sep_2026.xlsx")
    if not os.path.exists(file_path):
        print(f"[WARN] GL file not found: {file_path}")
        return 0

    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb["GL Apr-Sep"]

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    rows = list(ws.iter_rows(values_only=True))
    for r in rows[3:]:
        if not r or not r[0]:
            continue
        txn_date = str(r[0]).strip()
        voucher = str(r[1]).strip() if r[1] else ""
        vendor = str(r[2]).strip() if r[2] else ""
        ref = str(r[3]).strip() if r[3] else ""
        cost_centre = str(r[4]).strip() if r[4] else ""
        amount = float(r[5]) if r[5] is not None else 0.0
        narration = str(r[6]).strip() if r[6] else ""
        entered_by = str(r[7]).strip() if r[7] else ""

        cur.execute("""
            INSERT INTO general_ledger (txn_date, voucher, vendor, ref, cost_centre, amount, narration, entered_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (txn_date, voucher, vendor, ref, cost_centre, amount, narration, entered_by))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} GL entries from GL_Export_Apr-Sep_2026.xlsx.")
    return count


def ingest_emails():
    """Ingest .eml files from Day 1 Email."""
    email_dir = os.path.join(DAY1_DIR, "data_room", "email")
    if not os.path.exists(email_dir):
        print(f"[WARN] Email directory not found: {email_dir}")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    for fname in sorted(os.listdir(email_dir)):
        if not fname.endswith(".eml"):
            continue
        file_path = os.path.join(email_dir, fname)
        with open(file_path, "r", encoding="utf-8") as f:
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
    print(f"[INFO] Ingested {count} emails from data_room/email.")
    return count


def ingest_board_updates():
    """Ingest PDF Board updates from Day 1 Documents."""
    docs_dir = os.path.join(DAY1_DIR, "data_room", "documents")
    if not os.path.exists(docs_dir):
        print(f"[WARN] Documents directory not found: {docs_dir}")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    for fname in sorted(os.listdir(docs_dir)):
        if not fname.endswith(".pdf"):
            continue
        file_path = os.path.join(docs_dir, fname)
        reader = pypdf.PdfReader(file_path)
        full_text = "\n".join(p.extract_text() for p in reader.pages)

        # Parse period and metrics from text
        period = "Apr to Jun 2026" if "Apr to Jun" in full_text else "Jul to Sep 2026"
        sent_date = "2026-07-08" if "8 Jul 2026" in full_text else "2026-10-06"
        
        # Regex extraction
        arr_match = re.search(r"ARR\s*\(recurring\)\s*\n?Rs\.\s*([\d\.]+\s*Cr)", full_text)
        arr = f"Rs. {arr_match.group(1)}" if arr_match else None

        cust_match = re.search(r"Customers\s*\n?(\d+)", full_text)
        customers = int(cust_match.group(1)) if cust_match else None

        team_match = re.search(r"Team\s*\n?(\d+)", full_text)
        team_size = int(team_match.group(1)) if team_match else None

        burn_match = re.search(r"Monthly burn\s*\n?Rs\.\s*([\d\.]+\s*L)", full_text)
        monthly_burn = f"Rs. {burn_match.group(1)}" if burn_match else None

        runway_match = re.search(r"Runway\s*\n?(\d+\s*months)", full_text)
        runway = runway_match.group(1) if runway_match else None

        cur.execute("""
            INSERT INTO board_updates (filename, period, sent_date, arr, customers, team_size, monthly_burn, runway, full_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fname, period, sent_date, arr, customers, team_size, monthly_burn, runway, full_text))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} board updates from data_room/documents.")
    return count


def read_docx(file_path):
    """Helper to extract text from a docx file."""
    with zipfile.ZipFile(file_path) as z:
        tree = ET.fromstring(z.read("word/document.xml"))
        return "".join(node.text for node in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text)


def ingest_transcripts():
    """Ingest T1 and T2 docx files from Day 1 Transcripts."""
    t_dir = os.path.join(DAY1_DIR, "transcripts")
    if not os.path.exists(t_dir):
        print(f"[WARN] Transcripts directory not found: {t_dir}")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()
    count = 0

    transcripts = [
        ("T1", "T1_CEO_Kickoff_Call.docx", "CEO kickoff call"),
        ("T2", "T2_CFO_Call.docx", "CFO call")
    ]

    for call_id, fname, default_title in transcripts:
        fpath = os.path.join(t_dir, fname)
        if not os.path.exists(fpath):
            continue
        text = read_docx(fpath)
        cur.execute("""
            INSERT INTO transcripts (call_id, title, full_text)
            VALUES (?, ?, ?)
        """, (call_id, default_title, text))
        count += 1

    conn.commit()
    conn.close()
    print(f"[INFO] Ingested {count} transcripts from transcripts/.")
    return count


def populate_evidence_index():
    """Populate initial evidence index table with references."""
    conn = get_db_connection()
    cur = conn.cursor()

    evidence_items = [
        ("E001", "Employee_Master.xlsx", "Sheet: Employees, Rows: 3-22", "Company active headcount is 19 employees across 5 departments", "Veloxa Employees", "2026-10-31", "HIGH"),
        ("E002", "Board_Update_Apr-Jun_2026.pdf", "Page 1, Key numbers", "Q1 ARR is Rs. 5.8 Cr, 61 customers, Team: 19, Burn: Rs. 46 L, Runway: 14 months", "Veloxa Board", "2026-07-08", "HIGH"),
        ("E003", "Board_Update_Jul-Sep_2026.pdf", "Page 1, Key numbers", "Q2 ARR is Rs. 6.1 Cr, 66 customers, Team: 19, Burn: Rs. 44 L, Runway: 13 months", "Veloxa Board", "2026-10-06", "HIGH"),
        ("E004", "GL_Export_Apr-Sep_2026.xlsx", "PAY-APR through PAY-SEP", "Monthly payroll expense is consistently Rs. 31,75,000", "Salaries (payroll)", "2026-04-28 to 2026-09-28", "HIGH"),
        ("E005", "GL_Export_Apr-Sep_2026.xlsx", "RENT-APR through RENT-SEP", "Monthly WeWork office rent is Rs. 2,36,000", "WeWork India", "2026-04-30 to 2026-09-30", "HIGH"),
        ("E006", "GL_Export_Apr-Sep_2026.xlsx", "JV-0421 to JV-0921", "AWS monthly cloud spend increased from Rs. 1,81,200 (Apr) to Rs. 2,48,310 (Sep)", "Amazon Web Services", "2026-04-08 to 2026-09-08", "HIGH"),
        ("E007", "GL_Export_Apr-Sep_2026.xlsx", "JV-0688", "Cohere Recruiting Partners paid Rs. 1,77,000 (50% advance for 2 backend roles)", "Cohere Recruiting Partners", "2026-06-30", "HIGH"),
        ("E008", "GL_Export_Apr-Sep_2026.xlsx", "JV-0846, JV-0904", "Logistics Summit marketing expenses totaled Rs. 10,03,000 across venue and catering", "Sapphire Events / Saphire Event Mgmt", "2026-08-29 to 2026-09-03", "HIGH"),
        ("E009", "GL_Export_Apr-Sep_2026.xlsx", "JV-0902", "External contractor Patil Infra Services paid Rs. 70,800 for on-call support 18-31 Aug", "Patil Infra Services", "2026-09-02", "HIGH"),
        ("E010", "Payroll_Register_Jan-Mar_2026.xlsx", "Payroll Q4, Row 22", "Rahul Verma paid full 28 days in Feb (Rs. 1,10,000) despite joining 3 Feb 2026", "Rahul Verma, Karthik Subramanian", "2026-02-28", "HIGH"),
        ("E011", "01.eml", "Email Body", "Karthik Subramanian ran Feb payroll using Jan sheet while Fatima was out", "Karthik Subramanian, Meera Iyer", "2026-02-28", "HIGH"),
        ("E012", "02.eml", "Email Body", "Rahul Verma emailed Fatima questioning higher than expected partial-month payslip", "Rahul Verma, Fatima Sheikh", "2026-03-06", "HIGH"),
        ("E013", "03.eml", "Email Body", "Fatima promised to check Rahul payslip query but no adjustment recorded in March", "Fatima Sheikh, Rahul Verma", "2026-03-10", "HIGH"),
        ("E014", "T1_CEO_Kickoff_Call.docx", "Meeting transcript", "Ananya says company is roughly 180 give or take, ARR 42-45 Cr, burn around 2.2", "Ananya Rao", "2026-11-16", "LOW"),
        ("E015", "T2_CFO_Call.docx", "Meeting transcript", "Meera claims burn is 2.2L/month, ARR at start was 48, salaries must not show to Ananya", "Meera Iyer", "2026-11-16", "LOW")
    ]

    for item in evidence_items:
        cur.execute("""
            INSERT OR REPLACE INTO evidence_index (ref_id, source_file, location, fact, entities, date_str, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, item)

    conn.commit()
    conn.close()
    print(f"[INFO] Populated {len(evidence_items)} core evidence items into evidence_index.")


def main():
    print("=== Starting Veloxa Day 1 Data Ingestion ===")
    init_database()
    ingest_employees()
    ingest_payroll()
    ingest_general_ledger()
    ingest_emails()
    ingest_board_updates()
    ingest_transcripts()
    populate_evidence_index()
    print("=== Day 1 Data Ingestion Completed Successfully ===")


if __name__ == "__main__":
    main()
