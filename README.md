# Carbon- and Latency-Aware Agent Workflow Scheduler

A smart scheduling system designed for **HackDays in MSRIT** that intelligently plans and routes multi-agent AI workflows across compute regions. It optimizes for minimal carbon footprint while satisfying execution latency and SLA constraints.

## Project Structure

```text
carbon-aware-agent-scheduler/
│
├── backend/
│   ├── __init__.py
│   ├── models.py
│   ├── scheduler.py
│   ├── optimizer.py
│   └── main.py
│
├── data/
│   ├── models.json
│   ├── regions.json
│   └── carbon.json
│
├── tests/
│   └── __init__.py
│
├── docs/
│   └── architecture.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Getting Started

### Prerequisites
- Python 3.10+

### Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn backend.main:app --reload
   ```
