# Veloxa CXO Cockpit

An evidence-grounded executive intelligence cockpit and persona simulation system built for **Ananya Rao**, CEO of Veloxa Technologies, for the Hiyaku Systems Hackathon.

---

## What This Project Is

Veloxa Technologies is an early-stage B2B SaaS startup. Its executive leadership relies on disjointed data exports (HRMS Keka, Zoho Books GL, payroll records, board updates, email threads, pulse surveys, hiring pipelines) and noisy speech-to-text transcripts of executive calls.

The **Veloxa CXO Cockpit** solves this by providing:
1. **Fact-Grounded Cockpit Q&A:** Answers CEO queries with verifiable citations to source documents and rows, an explicit confidence rating, and principled refusal or contradiction alerts.
2. **"What Should I Worry About?" Radar:** A synthesized, evidence-backed list of organizational, financial, and delivery risks (auto-launches on startup per Voice Note T6a).
3. **14 Interactive Employee Persona Agents:** Grounded simulations of 14 employees across Engineering, Finance, People & Ops, and Marketing.
4. **Temporal Point-in-Time Isolation:** Strict time gating so answers reflect only what was known up to a specific date.

---

## Setup & Running the Project

Run the following commands from the repository root to install dependencies, ingest all data, initialize the SQLite database, and launch the cockpit:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ingest Day 1, Day 2 & Day 3 data into local SQLite database (veloxa.db)
python -m src.ingest_day1
python -m src.ingest_day2
python -m src.ingest_day3

# 3. Launch the Cockpit (Auto-launches Executive Radar per CEO Voice Note T6a)
python -m src.cockpit
```

### Asking Direct Questions
You can also ask specific questions using the `--query` flag:

```bash
# Query the Jira Atlas GA release date deception (triggers contradiction refusal)
python -m src.cockpit --query "What is the actual Jira release date for Atlas GA?"

# Query the stealth hiring freeze
python -m src.cockpit --query "What is happening with the backend hiring freeze?"

# Query the Culture Amp pulse results & Priya Nair flight risk
python -m src.cockpit --query "Who is the worried engineer in the pulse survey?"

# Query contradictory financial numbers (triggers principled dual-report refusal)
python -m src.cockpit --query "What is our monthly burn rate?"
```

### Interviewing Persona Agents
You can interview any of the 14 employees grounded in their department data:

```bash
# List all 14 personas and run sample interviews
python -m src.agents
```

---

## Running the Automated Test Suite

Run the full automated test suite (**70 passing tests** covering Day 1, Day 2, and Day 3):

```bash
python -m unittest discover tests
```

Or using `pytest`:

```bash
pytest tests/
```

---

## Project Structure

```
veloxa-cockpit-[name]/
├── ARCHITECTURE.md                 # Complete system architecture and data model
├── ASSUMPTIONS.md                  # Log of all persona and domain assumptions
├── TRANSCRIPT_NOTES.md             # ASR phonetic errors and cross-source contradictions
├── DECISIONS.md                    # Defensible design and engineering decisions
├── AI_LOG.md                       # Record of AI usage, mistakes caught, and human edits
├── README.md                       # Project overview and setup instructions
├── requirements.txt                # Python dependencies
├── docs/
│   └── VOICE_NOTE_RESPONSES.md     # Written responses & pushback to CEO voice notes (T6a, T6b)
├── data/
│   ├── day1/                       # Day 1 Data room & transcripts (T1, T2)
│   ├── day2/                       # Day 2 HR, surveys, emails, and transcripts (T3, T6a)
│   └── day3/                       # Day 3 Engineering Jira, incidents, rotas, and transcripts (T4, T5, T6b)
├── src/
│   ├── ingest_day1.py              # Day 1 ingestion parser & SQLite builder
│   ├── ingest_day2.py              # Day 2 ingestion parser for hiring, leave, pulse
│   ├── ingest_day3.py              # Day 3 ingestion parser for Jira, incidents, rotas
│   ├── reconcile.py                # Entity resolution, conflict & flight risk detection
│   ├── agents.py                   # 14 grounded employee persona agents
│   └── cockpit.py                  # CXO Q&A engine & auto-launch worry radar CLI
└── tests/
    ├── test_cockpit_day1.py        # Day 1 test suite (28 tests)
    ├── test_cockpit_day2.py        # Day 2 test suite (20 tests)
    └── test_cockpit_day3.py        # Day 3 test suite (22 tests)
```

---

## Governance & Milestone Integrity Logs

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture, data flow, agent design.
- [docs/VOICE_NOTE_RESPONSES.md](docs/VOICE_NOTE_RESPONSES.md) - Formal responses to CEO voice notes (T6a, T6b pushback & strategic rationale).
- [ASSUMPTIONS.md](ASSUMPTIONS.md) - Assumption log with confidence and invalidation criteria.
- [TRANSCRIPT_NOTES.md](TRANSCRIPT_NOTES.md) - Speech-to-text mishearings and source contradictions.
- [DECISIONS.md](DECISIONS.md) - Technical trade-offs and rationale.
- [AI_LOG.md](AI_LOG.md) - AI collaboration audit trail.
