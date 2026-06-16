import streamlit as st
from src.ui import apply_global_style, page_header, module_card, metric_card, section, render_agent_flow_animation

st.set_page_config(
    page_title="Agentic AI Resilience Lab",
    page_icon="🛡️",
    layout="wide",
)

apply_global_style()

page_header(
    "Agentic AI Resilience Lab",
    "Failure propagation, observability, and recovery for multi-agent AI workflows. "
    "This project demonstrates how small reasoning, context, or verification errors can cascade across agents, "
    "and how engineering controls can reduce operational risk."
)
render_agent_flow_animation(
    title="Agentic AI workflow",
    subtitle="End-to-end multi-agent incident workflow",
    stop_agent="Report Agent",
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card("System focus", "Multi-agent AI", "Enterprise workflow reliability")

with col2:
    metric_card("Core risk", "Cascade failure", "One bad output can spread")

with col3:
    metric_card("Control layer", "EvidenceGate", "Verify before action")

with col4:
    metric_card("Demo mode", "Streamlit", "Interactive engineering lab")

section(
    "Why this lab exists",
    "Agentic systems are not only chatbots. In enterprise settings, agents may classify incidents, retrieve logs, "
    "call tools, recommend actions, and produce reports. The risk is that one weak step can contaminate later steps. "
    "This lab treats multi-agent AI as an engineering system that needs tracing, evidence checks, permissions, and recovery."
)

st.divider()

section("Main modules")

c1, c2, c3 = st.columns(3)

with c1:
    module_card(
        "1. Enterprise Incident Workflow",
        "A realistic IT outage workflow showing how triage, log analysis, knowledge retrieval, action recommendation, "
        "verification, safety control, and reporting work together.",
        ["IT operations", "agent workflow", "industrial scenario"],
    )

with c2:
    module_card(
        "2. Cascade Simulator",
        "Simulates how a wrong assumption, hallucinated claim, missing evidence, or injected instruction can spread "
        "from one agent to the next.",
        ["blast radius", "propagation depth", "failure path"],
    )

with c3:
    module_card(
        "3. AgentWatch Tracing",
        "Captures step-level traces, agent handoffs, evidence status, risk scores, and root-cause indicators.",
        ["observability", "trace logs", "root cause"],
    )

c4, c5, c6 = st.columns(3)

with c4:
    module_card(
        "4. Chaos Dashboard",
        "Injects controlled failures into the workflow and measures detection, containment, and recovery behaviour.",
        ["chaos testing", "recovery", "metrics"],
    )

with c5:
    module_card(
        "5. MAST Classifier",
        "Classifies multi-agent failures into practical categories such as incorrect verification, task derailment, "
        "unsafe delegation, and premature closure.",
        ["taxonomy", "classification", "failure analysis"],
    )

with c6:
    module_card(
        "6. CASCADE Isolation",
        "Quarantines risky outputs, blocks unsupported claims, and prevents contaminated context from spreading downstream.",
        ["isolation", "containment", "safety gate"],
    )

st.divider()

section(
    "How to use the demo",
    "Start with the Enterprise Incident Workflow page. Run the normal workflow first, then inject a failure. "
    "After that, use the module pages to inspect propagation, tracing, classification, and containment."
)

st.info(
    "This is an applied portfolio project for AI engineering, agentic AI reliability, observability, and safety-oriented system design."
)