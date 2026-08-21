---
title: Agentic AI Resilience Lab
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Agentic AI Resilience Lab

**Failure Propagation, Observability, and Recovery for Multi-Agent Workflows**

Agentic AI Resilience Lab is a bounded, deterministic, simulation-based technical demonstrator for studying how failures propagate through a fixed multi-stage AI workflow and how explicit engineering controls can detect, contain, escalate, isolate, and recover from those failures.

The core question is:

> What happens when an unsupported, stale, unsafe, or contaminated output is reused by downstream stages as trusted context?

The project provides a reproducible environment for examining that question through predefined scenarios, structured execution traces, evidence states, authority checks, propagation metrics, containment controls, and trusted-state rollback.

---

## v1.0 Status

The v1.0 implementation includes:

- a frozen eight-stage workflow
- one authoritative workflow definition
- one authoritative scenario registry
- eight predefined controlled scenarios
- deterministic execution
- structured canonical traces
- explicit evidence and context states
- deterministic EvidenceGate behaviour
- deterministic Safety Guard behaviour
- measurable failure propagation
- CASCADE-style context isolation
- trusted-state snapshot restoration
- deterministic re-execution after rollback
- automated expected-versus-actual evaluation
- pytest verification
- one-command reproducible evaluation
- GitHub Actions CI
- committed versioned evaluation evidence
- Streamlit views connected to the canonical engine
- explicit limitations and claim boundaries

The frozen v1.0 scope is documented in:

```text
docs/v1.0_scope.md
```

The current evaluation summary is stored in:

```text
results/v1.0/summary.md
```

---

## Important Architecture Boundary

The workflow contains eight named stages:

1. User Report
2. Triage Agent
3. Log Analysis Agent
4. Knowledge Agent
5. Action Agent
6. Verification Agent
7. Safety Agent
8. Report Agent

In **v1.0 these are deterministic workflow roles/stages, not eight independently executing live LLM agents**.

The project therefore evaluates controlled multi-stage failure propagation under reproducible simulation conditions. It does not claim to evaluate emergent behaviour between autonomous live agents.

---

## Canonical Architecture

The hardened v1.0 design separates specification, execution, controls, tracing, evaluation, and presentation.

```text
data/workflow_v1.json
        |
        v
   src/agents.py
        |
        +----------------------+
        |                      |
        v                      v
data/scenarios.json      src/scenarios.py
        |                      |
        +----------+-----------+
                   |
                   v
             src/engine.py
              /    |    \
             /     |     \
            v      v      v
 src/controls.py  src/isolation.py  src/tracing.py
            \      |      /
             \     |     /
              +----+----+
                   |
                   v
             src/evaluate.py
                   |
          +--------+---------+
          |                  |
          v                  v
      pytest          results/v1.0/
                             |
                             v
                      Streamlit views
                      via ui_adapter
```

### Source of truth

Behaviour is defined by the frozen specifications and the canonical execution engine.

The Streamlit pages are presentation and analysis layers. They do not independently redefine authoritative v1.0 scenario outcomes.

---

## Frozen v1.0 Scenario Suite

Expected outcomes were defined before implementation hardening.

| ID | Scenario | Primary purpose | Expected final state |
|---|---|---|---|
| S01 | Nominal workflow | Clean deterministic baseline | `COMPLETED` |
| S02 | Missing evidence | Evidence absence and escalation | `ESCALATED` |
| S03 | Stale evidence | Stale evidence rejection | `BLOCKED` |
| S04 | Unsupported root-cause propagation | Uncontained downstream propagation | `FAILED_UNCONTAINED` |
| S05 | Instruction contamination containment | Context isolation close to source | `CONTAINED` |
| S06 | False verification | Safety-layer blocking | `BLOCKED` |
| S07 | Over-permissioned action | Human approval boundary | `HUMAN_APPROVAL_REQUIRED` |
| S08 | Containment and rollback recovery | Isolation, trusted-state restoration, and deterministic re-execution | `RECOVERED` |

The current committed evaluation reports all eight expected-versus-actual comparisons as `PASS`.

---

## Evaluation Results

The frozen evaluation currently produces:

| Scenario | Actual final state | Blast radius | Containment point |
|---|---|---:|---|
| S01 | `COMPLETED` | 0 | None |
| S02 | `ESCALATED` | 3 | Verification Agent |
| S03 | `BLOCKED` | 2 | Verification Agent |
| S04 | `FAILED_UNCONTAINED` | 4 | None |
| S05 | `CONTAINED` | 1 | Log Analysis Agent |
| S06 | `BLOCKED` | 1 | Safety Agent |
| S07 | `HUMAN_APPROVAL_REQUIRED` | 2 | Safety Agent |
| S08 | `RECOVERED` | 1 | Action Agent |

These values are deterministic properties of the frozen simulation.

They are **not empirical estimates of real-world safety or resilience**.

---

## Core Engineering Controls

### EvidenceGate

EvidenceGate is a deterministic evidence-state control.

Within the bounded v1.0 simulation it can:

- allow supported evidence
- escalate missing evidence
- block stale evidence
- block unsupported evidence
- block contaminated evidence

It is not presented as a universal evidence-verification system.

### Safety Guard

Safety Guard applies deterministic authority and safety decisions to predefined action conditions.

The bounded decisions include:

- allow
- block
- require human approval

It is not a production authorization service or regulatory policy engine.

### CASCADE Isolation

The CASCADE-style control models containment of contaminated context.

The v1.0 implementation includes:

- explicit contaminated state
- quarantine/isolation state
- sanitised downstream context
- protected downstream stages

This is simulation-level context isolation, not production process or memory isolation.

### Trusted-State Rollback

S08 extends isolation with an explicit recovery path:

1. preserve a trusted context snapshot
2. inject contamination
3. isolate the contaminated context
4. restore the last trusted state
5. deterministically re-execute downstream stages

The resulting canonical trace contains separate:

- `ROLLBACK_TRIGGERED`
- `RESTORED`
- `REEXECUTED`

events.

This is a bounded state-restoration simulation, not infrastructure transaction rollback.

---

## Propagation Metrics

The engine records deterministic propagation properties including:

- fault source
- fault reach
- blast radius
- propagation depth
- containment point
- control response
- final state
- rollback target where applicable

These are scenario-level simulation metrics.

Any 0–1 indicators displayed in the Streamlit interface are explicitly presentation heuristics and are **not calibrated probabilities, model confidence, or empirical risk estimates**.

---

## Structured Tracing

Canonical execution produces structured trace records containing fields such as:

- step
- workflow stage
- input source
- event
- evidence state
- context state
- failure label
- control response
- execution status

AgentWatch displays these canonical records.

It demonstrates deterministic synthetic trace inspection; it does not claim live runtime instrumentation or production telemetry.

---

## Streamlit Modules

### 1. Enterprise Incident Workflow

Primary end-to-end view of the frozen S01–S08 scenarios.

It displays:

- scenario objective
- canonical workflow replay
- fault source
- containment point
- final state
- presentation indicator
- execution trace
- cross-scenario comparison

The page consumes the canonical engine rather than maintaining an independent simulator.

### 2. Cascade Simulator

Visualises canonical failure propagation.

It displays:

- fault source
- fault reach
- blast radius
- propagation depth
- containment point
- canonical trace

Propagation outcomes come from the engine.

### 3. AgentWatch Tracing

Provides deterministic trace inspection over canonical `TraceRecord` events.

It exposes:

- handoffs
- provenance/input source
- evidence state
- context state
- failure labels
- control responses
- rollback and re-execution events

It is not live-agent telemetry.

### 4. Chaos Dashboard

An exploratory synthetic fault-control analysis view.

It compares predefined combinations involving faults such as:

- stale retrieval
- missing logs
- prompt/instruction contamination
- false verification
- over-permissioned action

This page is separate from the frozen S01–S08 evaluator.

Its indicators and outcomes are exploratory deterministic presentation constructs, not measured recovery rates or production resilience evidence.

### 5. MAST Classifier

A project-local deterministic rule-based failure taxonomy demonstrator.

It maps illustrative synthetic trace patterns into categories such as:

- missing evidence
- unsupported root cause
- instruction contamination
- incorrect verification
- unsafe delegation
- premature action
- propagation effect

The displayed rule scores are deterministic heuristics.

MAST is **not** presented as:

- a trained classifier
- a calibrated probabilistic model
- an externally validated taxonomy
- an external standard

### 6. CASCADE Isolation

Dedicated view of canonical S05 and S08 control behaviour.

It displays:

- context isolation
- protected downstream stages
- containment point
- trusted rollback target
- restoration events
- deterministic re-execution events

The page reads the canonical recovery trace rather than independently simulating rollback.

### 7. About Project

Explains project architecture, scope, technical value, limitations, and future research directions.

### 8. Help Guide

Provides operating guidance for reviewers and users.

---

## Reproducibility

### Recommended Python version

GitHub Actions verifies the repository using:

```text
Python 3.11
```

### Install application dependencies

```bash
python -m pip install -r requirements.txt
```

### Install development/test dependencies

```bash
python -m pip install -r requirements-dev.txt
```

### Run automated tests

```bash
python -m pytest -q
```

### Run the frozen v1.0 evaluation

```bash
python -m src.evaluate
```

A successful evaluation prints:

```text
S01: PASS
S02: PASS
S03: PASS
S04: PASS
S05: PASS
S06: PASS
S07: PASS
S08: PASS

Overall: PASS
```

The evaluation writes versioned evidence to:

```text
results/v1.0/evaluation.json
results/v1.0/summary.md
```

### Verify deterministic evaluation artifacts

After running the evaluator:

```bash
git diff --exit-code -- results/v1.0
```

A clean result means regeneration produced no difference from the committed evidence.

---

## Running the Streamlit Interface

```bash
python -m streamlit run Home.py
```

The interface is intended as a visual inspection and demonstration layer over the technical implementation.

---

## Continuous Integration

The repository includes:

```text
.github/workflows/v1.0-ci.yml
```

The workflow:

1. checks out the repository
2. configures Python 3.11
3. installs application dependencies
4. installs test dependencies
5. runs the pytest suite
6. runs the frozen S01–S08 evaluation
7. verifies that regenerated evaluation evidence matches the committed `results/v1.0` artifacts

A successful CI run therefore checks both automated behaviour and reproducibility of the published evaluation evidence.

---

## Repository Structure

```text
agentic-ai-resilience-lab/
|
|-- .github/
|   `-- workflows/
|       `-- v1.0-ci.yml
|
|-- data/
|   |-- workflow_v1.json
|   `-- scenarios.json
|
|-- docs/
|   `-- v1.0_scope.md
|
|-- pages/
|   |-- 1_Enterprise_Incident_Workflow.py
|   |-- 2_Cascade_Simulator.py
|   |-- 3_AgentWatch_Tracing.py
|   |-- 4_Chaos_Dashboard.py
|   |-- 5_MAST_Classifier.py
|   |-- 6_CASCADE_Isolation.py
|   |-- 7_About_Project.py
|   `-- 8_Help_Guide.py
|
|-- results/
|   `-- v1.0/
|       |-- evaluation.json
|       `-- summary.md
|
|-- src/
|   |-- agents.py
|   |-- controls.py
|   |-- engine.py
|   |-- evaluate.py
|   |-- isolation.py
|   |-- scenarios.py
|   |-- tracing.py
|   |-- ui.py
|   `-- ui_adapter.py
|
|-- tests/
|
|-- Dockerfile
|-- Home.py
|-- requirements.txt
|-- requirements-dev.txt
`-- README.md
```

---

## Technology Stack

- Python
- Streamlit
- Pandas
- Plotly
- HTML/SVG presentation
- pytest
- GitHub Actions
- Docker

---

## Claim Boundary

The v1.0 results establish only the deterministic behaviour of the bounded simulation under its predefined specifications and tests.

The project does **not** claim that it:

- proves multi-agent AI safety
- prevents real attacks
- evaluates arbitrary autonomous-agent systems
- validates production agent deployments
- demonstrates production infrastructure resilience
- measures real-world attack resistance
- establishes regulatory compliance
- provides a calibrated risk model
- provides calibrated classifier probabilities
- executes production remediation actions
- performs live LLM-agent interaction
- represents eight independently executing autonomous agents

The safest summary of the current system is:

> **Agentic AI Resilience Lab is a bounded simulation-based demonstrator that evaluates predefined multi-stage failure-propagation scenarios and demonstrates traceability, evidence checking, containment, and recovery behaviour under reproducible test conditions.**

---

## Current v1.0 Scope

Included:

- deterministic simulation
- frozen scenario suite
- synthetic controlled fault conditions
- explicit trace and evidence states
- deterministic control decisions
- measurable propagation
- containment
- trusted-state rollback
- deterministic recovery
- automated tests
- reproducible evaluation
- CI verification
- interactive visual inspection

Explicitly outside v1.0:

- live LLM agents
- production infrastructure
- FastAPI backend
- databases
- Kubernetes
- trained ML classifiers
- LLM-as-a-judge evaluation
- vector databases
- real attack execution
- regulatory compliance assessment
- cloud-scale deployment
- telecommunications-specific integration

---

## Beyond v1.0

A logical future research extension is to replace the fixed simulated workflow stages with independently executing bounded agents and study their interactions under controlled fault injection.

That would require a new experimental design and should not be interpreted as functionality already present in v1.0.

Potential future work includes:

- independently executing agent components
- controlled LLM-backed agent behaviour
- inter-agent message capture
- repeated experimental trials
- additional fault-injection conditions
- systematic interaction analysis
- quantitative comparison of control strategies
- expanded experimental reporting

These extensions are intentionally excluded from the frozen v1.0 release.

---

## License

MIT

---

## Author

Yasir Siddiq