import streamlit as st
import pandas as pd

from src.ui import apply_global_style, page_header, metric_card, section

st.set_page_config(
    page_title="About Project",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


page_header(
    "About Agentic AI Resilience Lab",
    "An applied engineering lab for simulating, tracing, classifying, and containing failure propagation in multi-agent AI workflows.",
)

st.markdown(
    """
    <div class="module-card">
        <h3>Project purpose</h3>
        <p>
        Agentic AI systems are increasingly used to coordinate tasks, retrieve information, call tools, verify outputs,
        and produce operational decisions. This project explores a practical problem: what happens when one agent produces
        a wrong, unsafe, unsupported, or contaminated output and downstream agents reuse it as trusted context?
        </p>
        <p>
        The lab provides a controlled environment for testing failure propagation, observability, recovery, taxonomy-based
        diagnosis, and semantic isolation in a realistic enterprise-style incident workflow.
        </p>
        <span class="tag">multi-agent AI</span>
        <span class="tag">observability</span>
        <span class="tag">failure propagation</span>
        <span class="tag">AI engineering</span>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Project type", "Applied lab", "Engineering simulation, not a chatbot demo")

with m2:
    metric_card("Core workflow", "IT incident", "Enterprise-style outage resolution")

with m3:
    metric_card("Main risk", "Cascade failure", "Small error propagates downstream")

with m4:
    metric_card("Main control", "Isolation", "Quarantine and recovery mechanisms")

st.divider()

section(
    "Why this project matters",
    "Multi-agent systems can fail in ways that are different from single-agent chatbots. "
    "The risk is not only one wrong response. The risk is that one wrong response becomes input for another agent, "
    "then influences decisions, recommendations, reports, or tool actions."
)

st.markdown(
    """
    <div class="module-card">
        <h3>Industrial problem addressed</h3>
        <p>
        In enterprise systems, agentic workflows may handle tickets, logs, runbooks, policy checks, approvals, reports,
        and remediation actions. If agents share unsupported context without verification, the system can produce
        confident but unsafe operational outcomes.
        </p>
        <p>
        This lab models that risk through controlled fault injection and shows how engineering controls such as evidence
        checks, traceability, permission boundaries, quarantine, and rollback can reduce blast radius.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

section("Project modules")

modules = pd.DataFrame(
    [
        {
            "module": "Enterprise Incident Workflow",
            "purpose": "Models a realistic IT outage scenario using concrete enterprise agent roles.",
            "engineering_value": "Shows the end-to-end workflow that all other modules analyse.",
        },
        {
            "module": "Cascade Simulator",
            "purpose": "Simulates how a faulty output spreads across downstream agents.",
            "engineering_value": "Measures blast radius, propagation depth, and containment point.",
        },
        {
            "module": "AgentWatch Tracing",
            "purpose": "Records step-level traces, evidence sources, risk scores, and root-cause candidates.",
            "engineering_value": "Adds observability and auditability to the agent workflow.",
        },
        {
            "module": "Chaos Dashboard",
            "purpose": "Injects controlled failures and compares recovery strategies.",
            "engineering_value": "Tests resilience under missing evidence, stale retrieval, prompt injection, and permission faults.",
        },
        {
            "module": "MAST Classifier",
            "purpose": "Classifies failure patterns into practical taxonomy categories.",
            "engineering_value": "Turns raw traces into structured failure labels and recommended controls.",
        },
        {
            "module": "CASCADE Isolation",
            "purpose": "Quarantines contaminated context and protects downstream agents.",
            "engineering_value": "Demonstrates semantic fault isolation and rollback-style recovery.",
        },
    ]
)

st.dataframe(
    modules,
    use_container_width=True,
    hide_index=True,
    height=280,
)

st.divider()

section("Architecture overview")

arch_col1, arch_col2 = st.columns(2)

with arch_col1:
    st.markdown(
        """
        <div class="module-card">
            <h3>Agent workflow layer</h3>
            <p>
            The workflow uses concrete enterprise roles:
            User Report, Triage Agent, Log Analysis Agent, Knowledge Agent, Action Agent,
            Verification Agent, Safety Agent, and Report Agent.
            </p>
            <span class="tag">agent workflow</span>
            <span class="tag">handoffs</span>
            <span class="tag">enterprise scenario</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with arch_col2:
    st.markdown(
        """
        <div class="module-card">
            <h3>Control layer</h3>
            <p>
            The control layer includes EvidenceGate verification, safety checks, risk scoring,
            provenance tracing, failure classification, context quarantine, and rollback simulation.
            </p>
            <span class="tag">verification</span>
            <span class="tag">policy control</span>
            <span class="tag">semantic isolation</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

section("Technology stack")

tech = pd.DataFrame(
    [
        {"area": "Application", "tools": "Streamlit"},
        {"area": "Programming", "tools": "Python"},
        {"area": "Data handling", "tools": "Pandas"},
        {"area": "Visualization", "tools": "Plotly, HTML/SVG animation"},
        {"area": "Testing target", "tools": "pytest"},
        {"area": "Deployment target", "tools": "Hugging Face Spaces, GitHub, later Streamlit Cloud"},
        {"area": "Packaging target", "tools": "requirements.txt, Dockerfile"},
    ]
)

st.dataframe(
    tech,
    use_container_width=True,
    hide_index=True,
    height=260,
)

st.divider()

section("What this project demonstrates for AI engineering")

st.markdown(
    """
    <div class="module-card">
        <h3>AI engineering skills demonstrated</h3>
        <p>
        This project demonstrates multi-agent workflow design, failure-mode modelling, risk scoring,
        trace observability, structured execution logs, controlled fault injection, taxonomy-based diagnosis,
        evidence-based verification, and semantic containment of unsafe or unsupported context.
        </p>
        <p>
        It is designed as a portfolio project for AI Engineer, Agentic AI Engineer, AI Safety Engineering,
        AI Automation, and research-oriented software engineering roles.
        </p>
        <span class="tag">Python</span>
        <span class="tag">Streamlit</span>
        <span class="tag">agentic AI</span>
        <span class="tag">observability</span>
        <span class="tag">failure analysis</span>
        <span class="tag">AI reliability</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

section("Known limitations")

limitations = pd.DataFrame(
    [
        {
            "limitation": "Simulation-based",
            "explanation": "The current version uses controlled synthetic traces rather than live production logs.",
        },
        {
            "limitation": "Rule-based classification",
            "explanation": "The MAST classifier is an explainable baseline, not a trained ML classifier.",
        },
        {
            "limitation": "No live LLM agent execution yet",
            "explanation": "The current version focuses on workflow behaviour, observability, and failure simulation.",
        },
        {
            "limitation": "No real production tool calls",
            "explanation": "Actions are simulated to avoid unsafe execution and keep the demo reproducible.",
        },
    ]
)

st.dataframe(
    limitations,
    use_container_width=True,
    hide_index=True,
    height=240,
)

st.divider()

section("Future extensions")

future = pd.DataFrame(
    [
        {
            "extension": "LLM-backed agents",
            "value": "Replace simulated agent outputs with controlled LLM calls and safety wrappers.",
        },
        {
            "extension": "FastAPI backend",
            "value": "Expose simulation, tracing, classification, and isolation modules as API endpoints.",
        },
        {
            "extension": "Persistent trace storage",
            "value": "Save experiment runs as JSONL or SQLite records for comparison.",
        },
        {
            "extension": "Automated evaluation",
            "value": "Run repeated experiments and calculate detection rate, containment rate, and false approval rate.",
        },
        {
            "extension": "CI tests",
            "value": "Add pytest checks for risk scoring, taxonomy classification, and containment behaviour.",
        },
    ]
)

st.dataframe(
    future,
    use_container_width=True,
    hide_index=True,
    height=260,
)

st.divider()

section(
    "Summary",
    "Agentic AI Resilience Lab is an applied portfolio project that treats multi-agent AI as an engineering system. "
    "It does not only show successful agent collaboration. It tests what happens when agent collaboration fails, "
    "how failures propagate, and how evidence-based verification, observability, taxonomy classification, and isolation controls can reduce operational risk."
)