import streamlit as st

from src.ui import (
    apply_global_style,
    metric_card,
    module_card,
    page_header,
    render_agent_flow_animation,
    section,
)


st.set_page_config(
    page_title="Agentic AI Resilience Lab",
    page_icon="🛡️",
    layout="wide",
)

apply_global_style()


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

page_header(
    "Agentic AI Resilience Lab",
    (
        "Failure propagation, observability, containment, and "
        "recovery in a bounded deterministic multi-stage workflow."
    ),
)


render_agent_flow_animation(
    title="Frozen v1.0 workflow",
    subtitle="Eight deterministic workflow stages",
    stop_agent="Report Agent",
)


# ---------------------------------------------------------------------
# Project status
# ---------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:
    metric_card(
        "v1.0 model",
        "Deterministic",
        "Simulation-based execution",
    )


with col2:
    metric_card(
        "Scenario suite",
        "S01–S08",
        "Eight frozen scenarios",
    )


with col3:
    metric_card(
        "Control focus",
        "Evidence + authority",
        "Containment and escalation",
    )


with col4:
    metric_card(
        "Verification",
        "Reproducible",
        "pytest + evaluation + CI",
    )


# ---------------------------------------------------------------------
# Purpose
# ---------------------------------------------------------------------

section(
    "Why this lab exists",
    (
        "A failure in a multi-stage AI workflow can become more "
        "important when a downstream stage reuses an unsupported, "
        "stale, unsafe, or contaminated output as trusted context. "
        "This lab provides a controlled environment for examining "
        "that propagation process and the effect of explicit "
        "engineering controls."
    ),
)


st.info(
    (
        "v1.0 models eight named workflow roles as deterministic "
        "stages. They are not eight independently executing live "
        "LLM agents."
    )
)


# ---------------------------------------------------------------------
# Main modules
# ---------------------------------------------------------------------

st.divider()

section(
    "Main modules",
    (
        "The primary workflow, cascade, tracing, and isolation "
        "views consume the canonical v1.0 execution engine."
    ),
)


c1, c2, c3 = st.columns(3)


with c1:
    module_card(
        "1. Enterprise Incident Workflow",
        (
            "End-to-end inspection of the frozen S01–S08 scenarios, "
            "including evidence state, containment, final state, "
            "execution trace, and cross-scenario comparison."
        ),
        [
            "canonical engine",
            "workflow trace",
            "scenario evaluation",
        ],
    )


with c2:
    module_card(
        "2. Cascade Simulator",
        (
            "Visualises canonical fault propagation, blast radius, "
            "propagation depth, containment point, and final state."
        ),
        [
            "blast radius",
            "propagation depth",
            "containment",
        ],
    )


with c3:
    module_card(
        "3. AgentWatch Tracing",
        (
            "Inspects canonical TraceRecord events, including "
            "handoffs, evidence state, context state, failure labels, "
            "control responses, restoration, and re-execution."
        ),
        [
            "synthetic tracing",
            "provenance",
            "recovery events",
        ],
    )


c4, c5, c6 = st.columns(3)


with c4:
    module_card(
        "4. Chaos Dashboard",
        (
            "Exploratory synthetic fault-control analysis separate "
            "from the frozen S01–S08 evaluator. Its 0–1 indicators "
            "are presentation heuristics, not calibrated risk."
        ),
        [
            "exploratory view",
            "fault conditions",
            "heuristic indicators",
        ],
    )


with c5:
    module_card(
        "5. MAST Classifier",
        (
            "Project-local deterministic rule-based taxonomy "
            "demonstrator for illustrative synthetic traces. "
            "It is not a trained or calibrated classifier."
        ),
        [
            "rule based",
            "failure taxonomy",
            "diagnostic view",
        ],
    )


with c6:
    module_card(
        "6. CASCADE Isolation",
        (
            "Inspects canonical S05 isolation and S08 trusted-state "
            "rollback behaviour, including isolation, restoration, "
            "and deterministic re-execution events."
        ),
        [
            "context isolation",
            "trusted-state rollback",
            "re-execution",
        ],
    )


# ---------------------------------------------------------------------
# Reproducible evidence
# ---------------------------------------------------------------------

st.divider()

section(
    "Reproducible v1.0 evidence",
    (
        "The hardened repository includes automated tests, a frozen "
        "scenario evaluator, committed evaluation artifacts, and "
        "GitHub Actions verification."
    ),
)


e1, e2 = st.columns(2)


with e1:
    with st.container(
        border=True
    ):
        st.markdown(
            "### Automated verification"
        )

        st.code(
            "python -m pytest -q",
            language="bash",
        )

        st.write(
            (
                "The test suite verifies specifications, controls, "
                "execution, isolation, recovery, evaluation, and "
                "canonical UI integration."
            )
        )


with e2:
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
                "The evaluator compares actual engine behaviour "
                "against the predefined S01–S08 expectations and "
                "writes versioned evidence under results/v1.0/."
            )
        )


# ---------------------------------------------------------------------
# Suggested review path
# ---------------------------------------------------------------------

st.divider()

section(
    "Suggested review path",
    (
        "For a concise technical review, start with the Enterprise "
        "Incident Workflow, then inspect propagation in Cascade, "
        "trace history in AgentWatch, and recovery in CASCADE "
        "Isolation."
    ),
)


review_path = [
    (
        "1",
        "Enterprise Incident Workflow",
        "Compare the eight frozen scenario outcomes.",
    ),
    (
        "2",
        "Cascade Simulator",
        "Inspect S04 uncontained propagation and S05 containment.",
    ),
    (
        "3",
        "AgentWatch Tracing",
        "Inspect S08 restoration and re-execution events.",
    ),
    (
        "4",
        "CASCADE Isolation",
        "Inspect S05 isolation and S08 rollback recovery.",
    ),
]


for number, title, description in review_path:
    with st.container(
        border=True
    ):
        st.markdown(
            f"**{number}. {title}**"
        )

        st.write(
            description
        )


# ---------------------------------------------------------------------
# Claim boundary
# ---------------------------------------------------------------------

st.divider()

section(
    "v1.0 claim boundary",
    (
        "Agentic AI Resilience Lab is a bounded simulation-based "
        "demonstrator. It evaluates predefined multi-stage "
        "failure-propagation scenarios and demonstrates traceability, "
        "evidence checking, containment, and recovery behaviour under "
        "reproducible test conditions."
    ),
)


st.warning(
    (
        "v1.0 does not demonstrate production multi-agent safety, "
        "live-agent telemetry, real attack prevention, regulatory "
        "compliance, production infrastructure resilience, or "
        "independently executing autonomous agents."
    )
)