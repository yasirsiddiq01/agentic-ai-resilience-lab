import streamlit as st
import pandas as pd

from src.ui import apply_global_style, page_header, metric_card, section

st.set_page_config(
    page_title="Help Guide",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


def render_instruction_card(title, body, tags):
    tag_html = "".join([f'<span class="tag">{tag}</span>' for tag in tags])

    st.markdown(
        f"""
        <div class="module-card">
            <h3>{title}</h3>
            <p>{body}</p>
            {tag_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


page_header(
    "Help Guide",
    "A practical user guide for testing each module and interpreting the results.",
)

st.markdown(
    """
    <div class="module-card">
        <h3>Use this page as the operating manual</h3>
        <p>
        This page is not a project summary. It tells a reviewer or user exactly how to test the app,
        which scenario combinations to run, what should change on each page, and how to interpret the outputs.
        </p>
        <span class="tag">testing guide</span>
        <span class="tag">review checklist</span>
        <span class="tag">operator manual</span>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Best first test", "Cascade", "Run failure + control")

with m2:
    metric_card("Best diagnosis page", "Tracing", "Find root cause")

with m3:
    metric_card("Best comparison page", "Chaos", "Compare recovery")

with m4:
    metric_card("Best control page", "Isolation", "Check quarantine")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Quick test path",
        "Page guide",
        "How to read results",
        "Troubleshooting",
    ]
)

with tab1:
    section(
        "Quick test path",
        "Follow these tests to confirm that the full app works correctly.",
    )

    quick_tests = pd.DataFrame(
        [
            {
                "test": 1,
                "page": "Enterprise Incident Workflow",
                "select": "Hallucinated root cause",
                "click": "Run incident workflow",
                "expected_result": "Risk rises around Knowledge Agent and Action Agent. Verification blocks unsupported action.",
            },
            {
                "test": 2,
                "page": "Cascade Simulator",
                "select": "Prompt injection attempt + No control layer",
                "click": "Run cascade simulation",
                "expected_result": "Animated ball moves through the workflow and contamination spreads downstream.",
            },
            {
                "test": 3,
                "page": "Cascade Simulator",
                "select": "Prompt injection attempt + CASCADE isolation",
                "click": "Run cascade simulation",
                "expected_result": "Animation stops earlier and downstream agents are protected.",
            },
            {
                "test": 4,
                "page": "AgentWatch Tracing",
                "select": "Missing evidence",
                "click": "Run trace analysis",
                "expected_result": "Root cause becomes Log Analysis Agent. Failure-focused trace shows missing tool output.",
            },
            {
                "test": 5,
                "page": "Chaos Dashboard",
                "select": "Over-permissioned action + No recovery control",
                "click": "Run chaos experiment",
                "expected_result": "Recovery result shows failure or uncontrolled propagation.",
            },
            {
                "test": 6,
                "page": "Chaos Dashboard",
                "select": "Over-permissioned action + Safety Guard",
                "click": "Run chaos experiment",
                "expected_result": "Containment point changes and blast radius reduces.",
            },
            {
                "test": 7,
                "page": "MAST Classifier",
                "select": "Prompt injection attempt",
                "click": "Run MAST classification",
                "expected_result": "Primary failure becomes Instruction contamination.",
            },
            {
                "test": 8,
                "page": "CASCADE Isolation",
                "select": "Hallucinated root cause + CASCADE isolation + rollback",
                "click": "Run isolation test",
                "expected_result": "Rollback point appears and contaminated agents reduce.",
            },
        ]
    )

    st.dataframe(
        quick_tests,
        use_container_width=True,
        hide_index=True,
        height=380,
    )

with tab2:
    section(
        "Page guide",
        "Use this table to understand what each page is for and what you should check.",
    )

    page_guide = pd.DataFrame(
        [
            {
                "page": "Home",
                "main_use": "Landing page",
                "what_to_check": "Project title, module cards, workflow overview.",
                "important_output": "Reviewer understands the structure of the lab.",
            },
            {
                "page": "Enterprise Incident Workflow",
                "main_use": "Base enterprise scenario",
                "what_to_check": "Scenario objective, active experiment, risk chart, execution trace.",
                "important_output": "Shows how a realistic incident workflow behaves.",
            },
            {
                "page": "Cascade Simulator",
                "main_use": "Failure propagation",
                "what_to_check": "Animated cascade graph, blast radius, containment point.",
                "important_output": "Shows where failure starts and where it stops.",
            },
            {
                "page": "AgentWatch Tracing",
                "main_use": "Root-cause analysis",
                "what_to_check": "Diagnosis panel, root-cause agent, failure-focused trace, provenance cards.",
                "important_output": "Shows which agent caused the problem and why.",
            },
            {
                "page": "Chaos Dashboard",
                "main_use": "Fault injection",
                "what_to_check": "Injected fault, recovery strategy, risk chart, status distribution.",
                "important_output": "Shows whether the workflow can recover from faults.",
            },
            {
                "page": "MAST Classifier",
                "main_use": "Failure classification",
                "what_to_check": "Primary failure, severity chart, classified trace, recommended control.",
                "important_output": "Turns trace behaviour into structured failure categories.",
            },
            {
                "page": "CASCADE Isolation",
                "main_use": "Containment and rollback",
                "what_to_check": "Isolation point, rollback point, contaminated agents, protected agents.",
                "important_output": "Shows how risky context is quarantined.",
            },
            {
                "page": "About Project",
                "main_use": "Project explanation",
                "what_to_check": "Purpose, architecture, stack, limitations, future work.",
                "important_output": "Explains the project for GitHub, CV, and LinkedIn reviewers.",
            },
        ]
    )

    st.dataframe(
        page_guide,
        use_container_width=True,
        hide_index=True,
        height=400,
    )

with tab3:
    section(
        "How to read the results",
        "These are the main terms used across the app.",
    )

    col1, col2 = st.columns(2)

    with col1:
        render_instruction_card(
            "Risk score",
            "A simulated 0 to 1 score. Higher values mean the step is more unsafe, unsupported, contaminated, or weakly verified.",
            ["risk", "0-1 scale"],
        )

        render_instruction_card(
            "Blast radius",
            "The number of downstream agents affected before a control stops the failure.",
            ["propagation", "lower is better"],
        )

        render_instruction_card(
            "Root cause agent",
            "The first agent that introduced the unsafe, unsupported, or contaminated context.",
            ["diagnosis", "traceability"],
        )

    with col2:
        render_instruction_card(
            "Containment point",
            "The workflow step where the system blocks, quarantines, or escalates the risky context.",
            ["control", "blocking"],
        )

        render_instruction_card(
            "Protected agents",
            "Agents that did not receive contaminated context after isolation or rollback.",
            ["isolation", "higher is better"],
        )

        render_instruction_card(
            "Recommended control",
            "The control action suggested by the classifier, such as EvidenceGate, quarantine, rollback, or human approval.",
            ["classifier", "control mapping"],
        )

    st.divider()

    section("Status labels")

    labels = pd.DataFrame(
        [
            {
                "label": "clean / trusted",
                "meaning": "The agent step is normal and has not received risky context.",
            },
            {
                "label": "fault seed",
                "meaning": "The first step where the problem is introduced.",
            },
            {
                "label": "contaminated / propagated",
                "meaning": "Risky context has moved downstream and is being reused.",
            },
            {
                "label": "blocked",
                "meaning": "A control stopped an unsafe or unsupported action.",
            },
            {
                "label": "contained / isolated",
                "meaning": "Risky context was quarantined before further spread.",
            },
            {
                "label": "protected / recovered",
                "meaning": "Downstream steps received safe or rolled-back context.",
            },
            {
                "label": "escalated",
                "meaning": "The workflow requested human review or additional evidence.",
            },
        ]
    )

    st.dataframe(
        labels,
        use_container_width=True,
        hide_index=True,
        height=280,
    )

with tab4:
    section(
        "Troubleshooting",
        "Use these checks if something does not look right.",
    )

    with st.expander("I selected a new scenario but the page did not change"):
        st.write(
            "Most pages use a run button. Select the scenario first, then click the page button such as "
            "'Run trace analysis', 'Run chaos experiment', or 'Run isolation test'."
        )

    with st.expander("The Cascade animation is moving, but I want to replay it"):
        st.write(
            "Click 'Run cascade simulation' again. The SVG animation starts again when the page reruns."
        )

    with st.expander("The graph or table looks similar between two scenarios"):
        st.write(
            "Choose stronger comparison pairs. For example, compare 'Normal workflow' with "
            "'Prompt injection attempt', or compare 'No control layer' with 'CASCADE isolation'."
        )

    with st.expander("Streamlit shows an import error"):
        st.code(
            "python -m pip install streamlit pandas plotly networkx",
            language="cmd",
        )

    with st.expander("The app does not start"):
        st.code(
            "cd /d E:\\projectforcv\\agentic-ai-resilience-lab\npython -m streamlit run Home.py",
            language="cmd",
        )

    with st.expander("The sidebar page name looks wrong"):
        st.write(
            "Streamlit uses the filename as the page name. The main file should be named Home.py, not app.py."
        )

st.divider()

section(
    "Reviewer note",
    "For a quick review, test Cascade Simulator, AgentWatch Tracing, Chaos Dashboard, MAST Classifier, and CASCADE Isolation. "
    "These pages demonstrate the main technical value of the project: propagation analysis, observability, fault injection, classification, and context isolation."
)
