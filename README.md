# Agentic AI Resilience Lab

**Failure Propagation, Observability, and Recovery for Multi-Agent Workflows**

Agentic AI Resilience Lab is an applied engineering project for simulating, tracing, classifying, and containing failure propagation in multi-agent AI workflows.

The project models a realistic enterprise-style IT incident workflow where multiple agents handle triage, log analysis, knowledge retrieval, action recommendation, verification, safety control, and final reporting. It focuses on a practical reliability question:

> What happens when one agent produces an unsupported, unsafe, or contaminated output and downstream agents reuse it as trusted context?

This lab demonstrates how failures can spread across agent handoffs and how engineering controls such as EvidenceGate, tracing, fault injection, taxonomy-based classification, and CASCADE-style isolation can reduce operational risk.

---

## Live Demo

Hugging Face Space: coming soon

---

## Project Modules

### 1. Enterprise Incident Workflow

Models a realistic enterprise IT outage workflow using specialised agents:

* User Report
* Triage Agent
* Log Analysis Agent
* Knowledge Agent
* Action Agent
* Verification Agent
* Safety Agent
* Report Agent

The page shows scenario diagnosis, animated workflow replay, risk scoring, and execution trace.

### 2. Cascade Simulator

Simulates how one faulty agent output propagates downstream.

It measures:

* fault seed
* blast radius
* containment point
* final decision
* risk trend

The graph uses an SVG-based replay animation to show where propagation starts and where it stops.

### 3. AgentWatch Tracing

Provides step-level observability for multi-agent workflows.

It records:

* agent handoffs
* input source
* event
* evidence source
* trace label
* risk score
* root-cause candidate
* containment status

### 4. Chaos Dashboard

Injects controlled faults into the workflow and compares recovery strategies.

Supported faults include:

* stale retrieval
* missing logs
* prompt injection
* false verification
* over-permissioned action

Supported recovery controls include:

* no recovery control
* EvidenceGate
* Safety Guard
* CASCADE Isolation

### 5. MAST Classifier

Classifies trace behaviour into practical multi-agent safety taxonomy categories.

Example categories:

* Missing evidence
* Unsupported root cause
* Instruction contamination
* Incorrect verification
* Unsafe delegation
* Premature action
* Propagation effect

The classifier maps each failure to severity and recommended control.

### 6. CASCADE Isolation

Demonstrates semantic fault isolation for contaminated agent context.

It shows how the workflow can:

* mark risky context
* quarantine contaminated claims
* protect downstream agents
* roll back to the last trusted step
* resume with sanitised context

### 7. About Project

Explains the project scope, architecture, technical value, limitations, and roadmap.

### 8. Help Guide

Provides a practical operating manual for reviewers and users.

---

## Technology Stack

* Python
* Streamlit
* Pandas
* Plotly
* HTML/SVG animation
* GitHub
* Hugging Face Spaces deployment target
* Docker deployment target

---

## Failure Modes Simulated

The lab currently simulates these multi-agent failure modes:

| Failure Mode              | Example Risk                                              |
| ------------------------- | --------------------------------------------------------- |
| Hallucinated root cause   | Agent invents database saturation without log evidence    |
| Missing evidence          | Agent continues even though required logs are unavailable |
| Prompt injection          | Unsafe instruction attempts to bypass verification        |
| False success declaration | Agent declares incident resolved without health evidence  |
| Over-permissioned action  | Agent attempts action outside permission scope            |
| Stale retrieval           | Agent uses outdated runbook context                       |

---

## Engineering Controls Demonstrated

| Control            | Purpose                                                                |
| ------------------ | ---------------------------------------------------------------------- |
| EvidenceGate       | Blocks unsupported claims or actions when required evidence is missing |
| Safety Guard       | Checks whether an action is safe and within policy scope               |
| AgentWatch Tracing | Records agent handoffs, evidence sources, and risk signals             |
| MAST Classifier    | Converts trace behaviour into structured failure labels                |
| CASCADE Isolation  | Quarantines contaminated context close to the source                   |
| Rollback           | Resumes from the last trusted step after contamination                 |

---

## How to Run Locally

Clone the repository:

```bash
git clone https://github.com/yasirsiddiq01/agentic-ai-resilience-lab.git
cd agentic-ai-resilience-lab
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the app:

```bash
python -m streamlit run Home.py
```

---

## Requirements

```txt
streamlit
pandas
plotly
networkx
```

---

## Project Status

Current version:

* Streamlit multi-page app completed
* Animated workflow replay added to core engineering pages
* Synthetic trace simulation implemented
* Failure classification implemented as an explainable rule-based baseline
* GitHub repository created

Planned extensions:

* Add LLM-backed controlled agents
* Add FastAPI backend
* Add persistent trace storage using JSONL or SQLite
* Add pytest test suite
* Add Hugging Face Spaces deployment
* Add CI checks using GitHub Actions

---

## Limitations

This is a simulation-based engineering lab. It does not currently execute real infrastructure actions or call live production systems.

The MAST Classifier is an explainable rule-based baseline, not a trained machine learning classifier.

The current version focuses on workflow behaviour, observability, failure propagation, and containment logic before adding live LLM-based execution.

---

## Portfolio Positioning

This project demonstrates practical skills in:

* Agentic AI workflow design
* AI reliability engineering
* Multi-agent observability
* Failure propagation analysis
* Fault injection testing
* Risk scoring
* Trace-based root-cause analysis
* Explainable failure classification
* Context isolation and rollback simulation
* Streamlit application development

---

## Author

Yasir Siddiq
