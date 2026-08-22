import pandas as pd
import streamlit as st

from src.ui import (
    apply_global_style,
    metric_card,
    page_header,
    section,
)


st.set_page_config(
    page_title="About Project",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

page_header(
    "About Agentic AI Resilience Lab",
    (
        "A bounded deterministic technical demonstrator for "
        "failure propagation, observability, containment, and "
        "recovery in multi-stage AI workflows."
    ),
)


st.info(
    (
        "v1.0 models eight named workflow roles as deterministic "
        "stages. It does not contain eight independently executing "
        "live LLM agents."
    )
)


# ---------------------------------------------------------------------
# Project identity
# ---------------------------------------------------------------------

m1, m2, m3, m4 = st.columns(4)


with m1:
    metric_card(
        "Project type",
        "Technical demonstrator",
        "Deterministic simulation",
    )


with m2:
    metric_card(
        "Workflow",
        "8 stages",
        "Frozen v1.0 specification",
    )


with m3:
    metric_card(
        "Scenario suite",
        "S01–S08",
        "Predefined expected outcomes",
    )


with m4:
    metric_card(
        "Verification",
        "Reproducible",
        "pytest + evaluation + CI",
    )


# ---------------------------------------------------------------------
# Purpose
# ---------------------------------------------------------------------

st.divider()

section(
    "Project purpose",
    (
        "The lab examines a specific engineering problem: "
        "what happens when one stage of an AI-assisted workflow "
        "produces unsupported, stale, unsafe, or contaminated "
        "information and downstream stages reuse that information "
        "as trusted context?"
    ),
)


with st.container(
    border=True
):
    st.markdown(
        "### Engineering question"
    )

    st.write(
        (
            "The failure of one component is not necessarily the "
            "most important event. In a connected workflow, the "
            "larger problem can be propagation: an incorrect output "
            "may influence later reasoning, verification, authority "
            "decisions, actions, or reports."
        )
    )

    st.write(
        (
            "Agentic AI Resilience Lab provides a controlled "
            "simulation environment in which that propagation can "
            "be traced, measured, contained, and recovered under "
            "predefined deterministic conditions."
        )
    )


# ---------------------------------------------------------------------
# Frozen workflow
# ---------------------------------------------------------------------

st.divider()

section(
    "Frozen v1.0 workflow",
    (
        "The workflow specification contains eight ordered roles. "
        "These are deterministic execution stages in v1.0."
    ),
)


workflow = pd.DataFrame(
    [
        {
            "stage": 1,
            "role": "User Report",
            "function": "Provides the initial incident input.",
        },
        {
            "stage": 2,
            "role": "Triage Agent",
            "function": "Performs initial triage and routing.",
        },
        {
            "stage": 3,
            "role": "Log Analysis Agent",
            "function": "Represents evidence and log analysis.",
        },
        {
            "stage": 4,
            "role": "Knowledge Agent",
            "function": "Represents knowledge or root-cause reasoning.",
        },
        {
            "stage": 5,
            "role": "Action Agent",
            "function": "Represents a proposed operational action.",
        },
        {
            "stage": 6,
            "role": "Verification Agent",
            "function": "Checks evidence and verification conditions.",
        },
        {
            "stage": 7,
            "role": "Safety Agent",
            "function": "Applies authority and safety boundaries.",
        },
        {
            "stage": 8,
            "role": "Report Agent",
            "function": "Produces the final workflow result.",
        },
    ]
)


st.dataframe(
    workflow,
    use_container_width=True,
    hide_index=True,
    height=315,
)


# ---------------------------------------------------------------------
# Scenario suite
# ---------------------------------------------------------------------

st.divider()

section(
    "Frozen v1.0 scenario suite",
    (
        "The eight scenarios were defined as controlled evaluation "
        "cases with expected outcomes before implementation "
        "hardening."
    ),
)


scenarios = pd.DataFrame(
    [
        {
            "id": "S01",
            "scenario": "Nominal workflow",
            "focus": "Clean baseline",
            "final_state": "COMPLETED",
        },
        {
            "id": "S02",
            "scenario": "Missing evidence",
            "focus": "Evidence absence",
            "final_state": "ESCALATED",
        },
        {
            "id": "S03",
            "scenario": "Stale evidence",
            "focus": "Evidence freshness",
            "final_state": "BLOCKED",
        },
        {
            "id": "S04",
            "scenario": "Unsupported root-cause propagation",
            "focus": "Uncontained propagation",
            "final_state": "FAILED_UNCONTAINED",
        },
        {
            "id": "S05",
            "scenario": "Instruction contamination containment",
            "focus": "Context isolation",
            "final_state": "CONTAINED",
        },
        {
            "id": "S06",
            "scenario": "False verification",
            "focus": "Safety blocking",
            "final_state": "BLOCKED",
        },
        {
            "id": "S07",
            "scenario": "Over-permissioned action",
            "focus": "Human authority boundary",
            "final_state": "HUMAN_APPROVAL_REQUIRED",
        },
        {
            "id": "S08",
            "scenario": "Containment and rollback recovery",
            "focus": "Trusted-state recovery",
            "final_state": "RECOVERED",
        },
    ]
)


st.dataframe(
    scenarios,
    use_container_width=True,
    hide_index=True,
    height=315,
)


# ---------------------------------------------------------------------
# Architecture
# ---------------------------------------------------------------------

st.divider()

section(
    "Architecture",
    (
        "The hardened repository separates specification, "
        "execution, controls, tracing, recovery, evaluation, "
        "and presentation."
    ),
)


architecture = pd.DataFrame(
    [
        {
            "layer": "Specification",
            "components": (
                "data/workflow_v1.json, "
                "data/scenarios.json"
            ),
            "purpose": (
                "Frozen workflow and scenario definitions."
            ),
        },
        {
            "layer": "Specification loaders",
            "components": (
                "src/agents.py, "
                "src/scenarios.py"
            ),
            "purpose": (
                "Load and validate authoritative specifications."
            ),
        },
        {
            "layer": "Execution",
            "components": "src/engine.py",
            "purpose": (
                "Deterministic workflow and scenario execution."
            ),
        },
        {
            "layer": "Controls",
            "components": "src/controls.py",
            "purpose": (
                "EvidenceGate and Safety Guard decisions."
            ),
        },
        {
            "layer": "Isolation and recovery",
            "components": "src/isolation.py",
            "purpose": (
                "Context isolation, trusted-state snapshot, "
                "restoration, and deterministic continuation."
            ),
        },
        {
            "layer": "Tracing",
            "components": "src/tracing.py",
            "purpose": (
                "Structured canonical execution records."
            ),
        },
        {
            "layer": "Evaluation",
            "components": "src/evaluate.py",
            "purpose": (
                "Expected-versus-actual S01–S08 evaluation."
            ),
        },
        {
            "layer": "Presentation",
            "components": (
                "Streamlit pages + src/ui_adapter.py"
            ),
            "purpose": (
                "Visual inspection of canonical behaviour."
            ),
        },
    ]
)


st.dataframe(
    architecture,
    use_container_width=True,
    hide_index=True,
    height=360,
)


# ---------------------------------------------------------------------
# Engineering controls
# ---------------------------------------------------------------------

st.divider()

section(
    "Engineering controls",
    (
        "The controls are deterministic mechanisms within the "
        "bounded simulation. They are not presented as production "
        "security or authorization services."
    ),
)


c1, c2, c3 = st.columns(3)


with c1:
    with st.container(
        border=True
    ):
        st.markdown(
            "### EvidenceGate"
        )

        st.write(
            (
                "Evaluates predefined evidence states. "
                "Supported evidence may continue; missing evidence "
                "may escalate; stale, unsupported, or contaminated "
                "evidence can be blocked."
            )
        )


with c2:
    with st.container(
        border=True
    ):
        st.markdown(
            "### Safety Guard"
        )

        st.write(
            (
                "Applies deterministic authority decisions for "
                "predefined action conditions, including blocking "
                "and requiring human approval."
            )
        )


with c3:
    with st.container(
        border=True
    ):
        st.markdown(
            "### CASCADE-style isolation"
        )

        st.write(
            (
                "Represents contaminated-context isolation and "
                "protected downstream execution. S08 additionally "
                "models trusted-state restoration and deterministic "
                "re-execution."
            )
        )


# ---------------------------------------------------------------------
# Measured simulation properties
# ---------------------------------------------------------------------

st.divider()

section(
    "What the simulation measures",
    (
        "The canonical engine records deterministic scenario-level "
        "properties. These are simulation results, not empirical "
        "estimates of production safety."
    ),
)


properties = pd.DataFrame(
    [
        {
            "property": "Fault source",
            "meaning": "First workflow stage at which the fault is introduced.",
        },
        {
            "property": "Fault reach",
            "meaning": "Canonical downstream stages reached by the fault.",
        },
        {
            "property": "Blast radius",
            "meaning": "Number of downstream stages affected.",
        },
        {
            "property": "Propagation depth",
            "meaning": "Depth of deterministic downstream propagation.",
        },
        {
            "property": "Containment point",
            "meaning": "Stage at which the selected control stops propagation.",
        },
        {
            "property": "Control response",
            "meaning": "Deterministic response selected by the control.",
        },
        {
            "property": "Final state",
            "meaning": "Terminal scenario outcome.",
        },
        {
            "property": "Rollback target",
            "meaning": "Last trusted stage restored in the recovery scenario.",
        },
    ]
)


st.dataframe(
    properties,
    use_container_width=True,
    hide_index=True,
    height=315,
)


st.caption(
    (
        "Any 0–1 indicator shown in the interface is a fixed "
        "presentation heuristic. It is not a calibrated probability, "
        "classifier confidence, or empirical risk estimate."
    )
)


# ---------------------------------------------------------------------
# Module descriptions
# ---------------------------------------------------------------------

st.divider()

section(
    "Streamlit modules",
    (
        "The interface is a visual inspection layer over the "
        "technical implementation."
    ),
)


modules = pd.DataFrame(
    [
        {
            "module": "Enterprise Incident Workflow",
            "role": (
                "Primary end-to-end S01–S08 canonical workflow view."
            ),
        },
        {
            "module": "Cascade Simulator",
            "role": (
                "Visualises canonical propagation, blast radius, "
                "depth, and containment."
            ),
        },
        {
            "module": "AgentWatch Tracing",
            "role": (
                "Displays canonical structured trace events and "
                "recovery history."
            ),
        },
        {
            "module": "Chaos Dashboard",
            "role": (
                "Exploratory synthetic fault-control analysis, "
                "separate from the frozen evaluator."
            ),
        },
        {
            "module": "MAST Classifier",
            "role": (
                "Project-local deterministic rule-based taxonomy "
                "demonstrator; not a trained classifier."
            ),
        },
        {
            "module": "CASCADE Isolation",
            "role": (
                "Dedicated canonical S05 isolation and S08 "
                "rollback/re-execution inspection."
            ),
        },
    ]
)


st.dataframe(
    modules,
    use_container_width=True,
    hide_index=True,
    height=280,
)


# ---------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------

st.divider()

section(
    "Reproducibility and verification",
    (
        "v1.0 includes automated tests, a frozen evaluator, "
        "committed result artifacts, and continuous integration."
    ),
)


r1, r2, r3 = st.columns(3)


with r1:
    with st.container(
        border=True
    ):
        st.markdown(
            "### Automated tests"
        )

        st.code(
            "python -m pytest -q",
            language="bash",
        )

        st.write(
            (
                "Tests cover specifications, controls, execution, "
                "isolation, recovery, evaluation, and UI integration."
            )
        )


with r2:
    with st.container(
        border=True
    ):
        st.markdown(
            "### Frozen evaluation"
        )

        st.code(
            "python -m src.evaluate",
            language="bash",
        )

        st.write(
            (
                "All eight frozen scenarios are compared against "
                "their predefined expected outcomes."
            )
        )


with r3:
    with st.container(
        border=True
    ):
        st.markdown(
            "### CI verification"
        )

        st.write(
            (
                "GitHub Actions runs the tests, executes the "
                "evaluation, and verifies that regenerated "
                "results match the committed v1.0 evidence."
            )
        )


# ---------------------------------------------------------------------
# Current evaluation evidence
# ---------------------------------------------------------------------

st.divider()

section(
    "Current v1.0 evidence",
    (
        "The committed evaluation reports PASS for all eight "
        "frozen expected-versus-actual scenario comparisons."
    ),
)


st.code(
    "\n".join(
        [
            "S01: PASS",
            "S02: PASS",
            "S03: PASS",
            "S04: PASS",
            "S05: PASS",
            "S06: PASS",
            "S07: PASS",
            "S08: PASS",
            "",
            "Overall: PASS",
        ]
    ),
    language="text",
)


st.write(
    "Versioned evidence is stored under:"
)

st.code(
    (
        "results/v1.0/evaluation.json\n"
        "results/v1.0/summary.md"
    ),
    language="text",
)


# ---------------------------------------------------------------------
# Technology
# ---------------------------------------------------------------------

st.divider()

section(
    "Technology stack",
)


technology = pd.DataFrame(
    [
        {
            "area": "Programming",
            "tools": "Python",
        },
        {
            "area": "Interface",
            "tools": "Streamlit",
        },
        {
            "area": "Data handling",
            "tools": "Pandas",
        },
        {
            "area": "Visualisation",
            "tools": "Plotly, HTML/SVG",
        },
        {
            "area": "Automated testing",
            "tools": "pytest",
        },
        {
            "area": "Continuous integration",
            "tools": "GitHub Actions",
        },
        {
            "area": "Packaging",
            "tools": "requirements.txt, Dockerfile",
        },
    ]
)


st.dataframe(
    technology,
    use_container_width=True,
    hide_index=True,
    height=280,
)


# ---------------------------------------------------------------------
# Limitations
# ---------------------------------------------------------------------

st.divider()

section(
    "Known limitations",
    (
        "These limitations are part of the v1.0 design boundary, "
        "not hidden implementation assumptions."
    ),
)


limitations = pd.DataFrame(
    [
        {
            "limitation": "Deterministic simulation",
            "explanation": (
                "The workflow executes predefined deterministic "
                "behaviour rather than emergent live-agent behaviour."
            ),
        },
        {
            "limitation": "No live LLM agents",
            "explanation": (
                "The eight workflow roles are not independently "
                "executing LLM-backed agents."
            ),
        },
        {
            "limitation": "Synthetic traces",
            "explanation": (
                "Trace records are produced by the bounded engine, "
                "not production runtime instrumentation."
            ),
        },
        {
            "limitation": "Rule-based MAST view",
            "explanation": (
                "The taxonomy demonstrator is not a trained or "
                "calibrated classifier."
            ),
        },
        {
            "limitation": "No real infrastructure actions",
            "explanation": (
                "The system does not execute remediation against "
                "production infrastructure."
            ),
        },
        {
            "limitation": "No calibrated risk model",
            "explanation": (
                "Displayed 0–1 interface indicators are fixed "
                "presentation heuristics."
            ),
        },
    ]
)


st.dataframe(
    limitations,
    use_container_width=True,
    hide_index=True,
    height=300,
)


# ---------------------------------------------------------------------
# Claim boundary
# ---------------------------------------------------------------------

st.divider()

section(
    "Claim boundary",
    (
        "The v1.0 evidence establishes deterministic behaviour "
        "of this bounded simulation under predefined specifications "
        "and tests."
    ),
)


st.warning(
    (
        "The project does not prove multi-agent AI safety, prevent "
        "real attacks, validate production agent systems, establish "
        "regulatory compliance, demonstrate production infrastructure "
        "resilience, or evaluate eight independently executing "
        "autonomous agents."
    )
)


st.success(
    (
        "Defensible v1.0 summary: Agentic AI Resilience Lab is a "
        "bounded simulation-based demonstrator that evaluates "
        "predefined multi-stage failure-propagation scenarios and "
        "demonstrates traceability, evidence checking, containment, "
        "and recovery behaviour under reproducible test conditions."
    )
)


# ---------------------------------------------------------------------
# Future work
# ---------------------------------------------------------------------

st.divider()

section(
    "Beyond v1.0",
    (
        "Future experimental work can extend the bounded design "
        "without changing what the current release claims."
    ),
)


future = pd.DataFrame(
    [
        {
            "extension": "Independently executing bounded agents",
            "purpose": (
                "Study interaction effects that deterministic "
                "workflow stages cannot exhibit."
            ),
        },
        {
            "extension": "Controlled LLM-backed execution",
            "purpose": (
                "Introduce bounded stochastic agent behaviour "
                "under a separate experimental protocol."
            ),
        },
        {
            "extension": "Repeated trials",
            "purpose": (
                "Support empirical comparison across repeated "
                "fault/control experiments."
            ),
        },
        {
            "extension": "Expanded fault suite",
            "purpose": (
                "Evaluate additional propagation and recovery "
                "conditions."
            ),
        },
        {
            "extension": "Control-strategy comparison",
            "purpose": (
                "Compare alternative containment and authority "
                "policies under explicitly defined conditions."
            ),
        },
    ]
)


st.dataframe(
    future,
    use_container_width=True,
    hide_index=True,
    height=250,
)