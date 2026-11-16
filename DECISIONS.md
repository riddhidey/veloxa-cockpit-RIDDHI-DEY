# Veloxa CXO Cockpit - Technical Decisions Log (`DECISIONS.md`)

This log documents technical, architectural, and business choices made where multiple valid approaches were available, explaining the trade-offs and our defense.

---

### D-001: Data Storage Choice — SQLite3 + JSON Evidence Index
* **Alternatives Considered:**
  1. *Vector Database / Embeddings (Chroma/FAISS):* Good for semantic search, but prone to fuzzy matching, non-deterministic retrieval, and opaque source attribution.
  2. *PostgreSQL / MySQL Server:* Heavyweight, requires external services, docker setup, or credentials, violating the "one-command setup from a fresh clone" rule.
  3. *In-Memory SQLite3 + Structured JSON Evidence Catalog:* Zero installation overhead, 100% deterministic, enables strict relational SQL queries (e.g. cross-referencing join dates with payroll days), and creates inspectable artifacts for reviewers.
* **Decision:** We chose **SQLite3 with JSON Evidence indexing**. It delivers reproducible, instant execution and allows precise audit trails.

---

### D-002: Hierarchy of Source Truth (Ledger First vs. Transcript First)
* **Context:** Transcripts are colloquial and contain machine transcription artifacts. Ledgers are structured but can contain clerical errors.
* **Decision:**
  * **Tier 1 (Highest Authority):** Primary system exports (Keka HRMS, Zoho Books General Ledger, Payroll register, Board presentations).
  * **Tier 2 (Secondary Corroboration):** Written correspondence (Email threads with explicit dates/headers).
  * **Tier 3 (Unverified Clues):** Spoken transcripts (T1, T2) and voice notes. They signal *intent*, *perception*, and *suspicion*, but cannot override Tier 1 ledgers unless corroborating evidence exists.
* **Defense:** In any real company, what was paid to the bank (payroll register) and filed in board minutes has legal and accounting weight over a CEO's conversational comment on a speakerphone.

---

### D-003: Refusal & Uncertainty Policy (What the Cockpit Refuses to Answer)
* **Alternatives Considered:**
  1. *Always give an answer:* Provide the most plausible number and mention other numbers in passing.
  2. *Refuse completely when any ambiguity exists:* Decline to answer any question that has conflicting data.
  3. *Principled Refusal with Dual Reporting:* When a user asks a question with conflicting evidence (e.g., *"What is our monthly burn?"*), the cockpit explicitly states that sources disagree, reports both numbers with citations, and refuses to pick a single number as undisputed fact.
* **Decision:** We chose **Option 3 (Principled Refusal with Dual Reporting)**. If data is completely missing (e.g., asking about Q4 metrics not yet released), the cockpit outputs *"I don't know - this information is not present in records up to 16 Nov 2026."*

---

### D-004: 14 Persona Roster Selection
* **Context:** The prompt states: *"start with 14 people across engineering, finance, HR and marketing, and make them feel like real colleagues with real lives, not spreadsheet rows."*
* **Alternatives Considered:**
  * Include Sales and Support members and drop some engineers.
  * Model all 19 people.
* **Decision:** We selected the exact 14 employees belonging to Engineering, Finance, People & Ops, and Marketing:
  - Engineering (5): Vikram Menon, Priya Nair, Arjun Das, Sneha Kulkarni, Rahul Verma.
  - Finance (3): Meera Iyer, Karthik Subramanian, Fatima Sheikh.
  - People & Ops (3): Deepa Joshi, Rohan Banerjee, Lakshmi Pillai.
  - Marketing (3): Nikhil Bose, Aisha Khan, Siddharth Mehta.
  - Excluded from the 14 personas: Ananya Rao (CEO/User), Sales (Manoj Kumar, Divya Reddy), Support (Imran Siddiqui, Kavya Narayan).
* **Defense:** Matches the prompt's explicit department list ("engineering, finance, HR and marketing") and headcount count (14).

---

### D-005: Persona Memory & Grounding Architecture
* **Alternatives Considered:**
  1. *Pure LLM Prompting with unconstrained creativity:* Leads to persona drift and ungrounded fabrications.
  2. *Strict Fact-Only Extraction:* Leads to dry, robotic responses that feel like spreadsheet rows.
  3. *Hybrid Grounding (Hard facts + Assumed Personal Nuances):* Hard data (salary, manager, tenure, leave, emails) is locked into SQLite. Human attributes (hobbies, communication style, current emotional state) are explicitly crafted, anchored in data room clues, and registered in `ASSUMPTIONS.md`.
* **Decision:** Hybrid Grounding. When an agent speaks, it never contradicts its hard data, and its personal flavor reflects verified context (e.g. Karthik feeling stressed about CFA prep, Fatima frustrated by payroll handover errors).
