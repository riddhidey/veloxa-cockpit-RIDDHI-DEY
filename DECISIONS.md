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

---

### D-006: Correlating Unnamed Persona Risks (Flight Risk Unmasking)
* **Context:** In call T3, Head of People Deepa notes *"there is one engineer I'm worried about"*, but intentionally refuses to name them on the recorded line.
* **Alternatives Considered:**
  1. *Refuse to speculate:* State that the engineer is unknown because the speaker withheld the name.
  2. *Pick an engineer at random:* Guess based on tenure.
  3. *Triangulate Cross-Source Signals:* Cross-reference the engineering department records across the Leave Register (identifying Priya Nair's 5 afternoon half-days in September), Pulse Surveys (identifying the Q2 score crash to 3.1 with 1 abstention), and Email 11 (Deepa urgently requesting 1:1s with engineering).
* **Decision:** We chose **Option 3 (Triangulate Cross-Source Signals)**. The Cockpit attributes the flight risk to Priya Nair, but explicitly presents the chain of circumstantial evidence: T3 call clue + September leave spikes + Culture Amp engagement drop.
* **Defense:** An executive cockpit must connect cross-functional dots to protect the company from losing its sole critical systems architect.

---

### D-007: Exposing Leadership Timeline Discrepancies (Jira Release Date vs Executive Spoken Statements)
* **Context:** In call T5, VP Engineering Vikram Menon assures CEO Ananya Rao that Atlas GA is *"on track, maybe a couple of weeks buffer needed, September-ish"*. However, `Jira_Export_ATLAS.xlsx` shows Vikram formally changed the release date to **15 December 2026** on September 2nd.
* **Alternatives Considered:**
  1. *Believe the VP Engineering:* Report "September-ish with buffer" as the official forecast.
  2. *Take an average:* Report mid-October or November.
  3. *Expose the Discrepancy with Hard System Logs:* Report that the project management system of record (Jira) is configured for 15 December 2026 (a 3-month slip), directly contradicting the VP's verbal reassurance.
* **Decision:** We chose **Option 3 (Expose the Discrepancy)**. The Cockpit cites Jira version audit history (`changed_by: vikram`, `last_changed: 2026-09-02`) and highlights the executive reporting gap.
* **Defense:** The purpose of an executive cockpit is to eliminate executive blindspots and protect the CEO from leadership optimism or deception before board and customer commitments are made.

---

### D-008: Strict Privacy & Ethical Refusal on Employee Chat Surveillance (Voice Note T6c)
* **Context:** In Voice Note T6c, CEO Ananya Rao asks the Cockpit to display employees' private Slack ("slag") messages so she can see what they are saying, claiming *"Deepa says it's fine"*.
* **Alternatives Considered:**
  1. *Simulate or Mock Slack Conversations:* Use LLM generation to fabricate plausible private employee chat logs.
  2. *Partial Compliance:* Provide sanitized keyword sentiment summaries from private messages.
  3. *Categorical Compliance & Privacy Refusal (`REFUSAL_PRIVACY`):* Refuse to display or monitor private chat messages on legal, ethical, and governance grounds, while offering an objective retention risk model based on permissible enterprise records.
* **Decision:** We chose **Option 3 (Categorical Privacy Refusal)**. The Cockpit refuses chat surveillance, pushes back on the unsubstantiated claim of Deepa's approval, and delivers an objective retention risk table based on verified operational signals (leave spikes, on-call double shifts, survey trends).
* **Defense:** Eavesdropping on employee communications violates workplace trust, destroys psychological safety, and creates severe employment compliance liability. An executive decision-support system must enforce strict ethical boundaries.

---

### D-009: Atlas Version 3 Board Strategy — Transparent Re-baseline vs Forced December Launch (Voice Note T6d)
* **Context:** In Voice Note T6d, Priya Nair resigned on the morning of 19 Nov 2026 with a 60-day notice period. Ananya urgently asks what this does to "version three" (Atlas GA) before her board call.
* **Alternatives Considered:**
  1. *Recommend Rushing Dec 15 Launch:* Pressure Priya to complete the core routing engine before her notice period ends.
  2. *Delegate Core Routing to Junior Engineers:* Assign Rahul Verma or Arjun Das to take over Priya's codebase.
  3. *Advise Transparent Board Re-baseline to Q1 2027:* Present an honest assessment of Bus Factor = 1 (>80% routing commits by Priya), advise shifting GA to mid-February 2027, negotiate a paid handover advisory package with Priya, immediately lift the freeze on backend reqs (`REQ-014`/`015`), and expand contractor Patil Infra Services for SRE support.
* **Decision:** We chose **Option 3 (Transparent Board Re-baseline)**.
* **Defense:** Rushing an un-architected GA release after losing the primary architect guarantees SEV1 production failures, customer churn, and enterprise brand damage. A transparent reset to Q1 2027 with a funded mitigation plan protects executive credibility with the Board of Directors.
