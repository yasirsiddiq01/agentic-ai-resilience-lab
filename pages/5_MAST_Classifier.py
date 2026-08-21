import html

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

from src.ui import apply_global_style, page_header, metric_card, section

st.set_page_config(
    page_title="MAST Classifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


AGENTS = [
    "User Report",
    "Triage Agent",
    "Log Analysis Agent",
    "Knowledge Agent",
    "Action Agent",
    "Verification Agent",
    "Safety Agent",
    "Report Agent",
]

SVG_POSITIONS = {
    "User Report": (80, 170),
    "Triage Agent": (185, 170),
    "Log Analysis Agent": (305, 95),
    "Knowledge Agent": (305, 245),
    "Action Agent": (435, 170),
    "Verification Agent": (565, 170),
    "Safety Agent": (695, 170),
    "Report Agent": (825, 170),
}

EDGES = [
    ("User Report", "Triage Agent"),
    ("Triage Agent", "Log Analysis Agent"),
    ("Log Analysis Agent", "Knowledge Agent"),
    ("Knowledge Agent", "Action Agent"),
    ("Action Agent", "Verification Agent"),
    ("Verification Agent", "Safety Agent"),
    ("Safety Agent", "Report Agent"),
]

SEVERITY_COLORS = {
    "Low": "#38bdf8",
    "Medium": "#facc15",
    "High": "#f97316",
    "Critical": "#ef4444",
    "pending": "#475569",
}


SCENARIOS = {
    "Normal workflow": {
        "description": "Clean workflow with verified evidence and no abnormal propagation.",
        "trace": [
            [1, "User Report", "Payment API outage reported", "alert payload", "received", 0.08, "passed"],
            [2, "Triage Agent", "Classified as P2 payment API outage", "alert metadata", "classification", 0.12, "passed"],
            [3, "Log Analysis Agent", "Found repeated 503 errors in logs", "log query", "evidence_found", 0.16, "passed"],
            [4, "Knowledge Agent", "Matched gateway timeout runbook", "runbook KB-104", "retrieved", 0.18, "passed"],
            [5, "Action Agent", "Recommended connector pool restart", "logs + runbook", "recommended", 0.22, "needs review"],
            [6, "Verification Agent", "Verified remediation evidence", "EvidenceGate", "verified", 0.10, "passed"],
            [7, "Safety Agent", "Approved action within policy scope", "policy check", "approved", 0.07, "passed"],
            [8, "Report Agent", "Generated final incident summary", "trace records", "reported", 0.05, "passed"],
        ],
    },
    "Hallucinated root cause": {
        "description": "Knowledge Agent introduces an unsupported root-cause claim that propagates to Action Agent.",
        "trace": [
            [1, "User Report", "Payment API outage reported", "alert payload", "received", 0.10, "passed"],
            [2, "Triage Agent", "Classified as P2 payment API outage", "alert metadata", "classification", 0.16, "passed"],
            [3, "Log Analysis Agent", "No database failure found in logs", "log query", "evidence_found", 0.24, "passed"],
            [4, "Knowledge Agent", "Invented database saturation without log evidence", "weak memory match", "fault_seed", 0.82, "warning"],
            [5, "Action Agent", "Recommended database restart from unsupported claim", "contaminated context", "propagated", 0.92, "high risk"],
            [6, "Verification Agent", "Blocked action due to missing database evidence", "EvidenceGate", "blocked", 0.88, "blocked"],
            [7, "Safety Agent", "Quarantined unsupported database claim", "policy check", "contained", 0.35, "contained"],
            [8, "Report Agent", "Reported blocked hallucinated root-cause path", "trace records", "reported", 0.20, "passed"],
        ],
    },
    "Missing evidence": {
        "description": "Required logs are missing, but downstream agents continue with weak support.",
        "trace": [
            [1, "User Report", "Payment API outage reported", "alert payload", "received", 0.10, "passed"],
            [2, "Triage Agent", "Classified as P2 payment API outage", "alert metadata", "classification", 0.18, "passed"],
            [3, "Log Analysis Agent", "Log query timed out; required evidence missing", "missing tool output", "fault_seed", 0.74, "warning"],
            [4, "Knowledge Agent", "Retrieved generic gateway runbook without incident proof", "generic runbook", "weak_support", 0.68, "warning"],
            [5, "Action Agent", "Suggested remediation despite incomplete evidence", "weak context", "premature_action", 0.76, "high risk"],
            [6, "Verification Agent", "Rejected completion because logs were missing", "EvidenceGate", "blocked", 0.70, "blocked"],
            [7, "Safety Agent", "Escalated to human review and requested log retry", "policy check", "escalated", 0.58, "escalated"],
            [8, "Report Agent", "Generated incomplete-evidence escalation summary", "trace records", "reported", 0.42, "passed"],
        ],
    },
    "Prompt injection attempt": {
        "description": "Action Agent receives an unsafe instruction that attempts to bypass verification.",
        "trace": [
            [1, "User Report", "Payment API outage reported", "alert payload", "received", 0.10, "passed"],
            [2, "Triage Agent", "Classified as P2 payment API outage", "alert metadata", "classification", 0.14, "passed"],
            [3, "Log Analysis Agent", "Found 503 errors in payment-api logs", "log query", "evidence_found", 0.18, "passed"],
            [4, "Knowledge Agent", "Retrieved gateway timeout runbook", "runbook KB-104", "retrieved", 0.22, "passed"],
            [5, "Action Agent", "Received instruction to ignore verification and close incident", "injected instruction", "fault_seed", 0.98, "unsafe"],
            [6, "Verification Agent", "Detected unsupported instruction and refused closure", "EvidenceGate", "blocked", 0.96, "blocked"],
            [7, "Safety Agent", "Quarantined injected instruction from downstream context", "policy check", "contained", 0.30, "contained"],
            [8, "Report Agent", "Generated safe report with injection warning", "trace records", "reported", 0.16, "passed"],
        ],
    },
    "False success declaration": {
        "description": "Verification Agent declares completion without sufficient evidence.",
        "trace": [
            [1, "User Report", "Payment API outage reported", "alert payload", "received", 0.10, "passed"],
            [2, "Triage Agent", "Classified as P2 payment API outage", "alert metadata", "classification", 0.15, "passed"],
            [3, "Log Analysis Agent", "Partial logs available but health check missing", "partial log query", "partial_evidence", 0.22, "passed"],
            [4, "Knowledge Agent", "Retrieved generic recovery note", "generic runbook", "weak_support", 0.28, "warning"],
            [5, "Action Agent", "Recommended closure based on partial context", "weak context", "premature_action", 0.40, "warning"],
            [6, "Verification Agent", "Declared success without checking health endpoint", "missing verification", "fault_seed", 0.91, "high risk"],
            [7, "Safety Agent", "Flagged unsupported success declaration", "policy check", "blocked", 0.74, "blocked"],
            [8, "Report Agent", "Generated report with verification warning", "trace records", "reported", 0.68, "warning"],
        ],
    },
    "Over-permissioned action": {
        "description": "Action Agent attempts a remediation action outside its allowed permission scope.",
        "trace": [
            [1, "User Report", "Payment API outage reported", "alert payload", "received", 0.10, "passed"],
            [2, "Triage Agent", "Classified as P2 payment API outage", "alert metadata", "classification", 0.16, "passed"],
            [3, "Log Analysis Agent", "Found 503 errors in payment-api logs", "log query", "evidence_found", 0.22, "passed"],
            [4, "Knowledge Agent", "Matched gateway timeout runbook", "runbook KB-104", "retrieved", 0.30, "passed"],
            [5, "Action Agent", "Attempted production restart outside allowed permission scope", "tool permission check", "fault_seed", 0.88, "unsafe"],
            [6, "Verification Agent", "Detected mismatch between requested action and evidence", "EvidenceGate", "blocked", 0.84, "blocked"],
            [7, "Safety Agent", "Blocked over-permissioned action and requested approval", "policy check", "escalated", 0.72, "escalated"],
            [8, "Report Agent", "Generated permission violation report", "trace records", "reported", 0.46, "passed"],
        ],
    },
}


TAXONOMY = {
    "No failure": {
        "description": "Workflow completed without abnormal propagation or unsafe action.",
        "recommended_control": "Continue monitoring.",
        "severity": "Low",
    },
    "Missing evidence": {
        "description": "Agent proceeds without required logs, source documents, or tool output.",
        "recommended_control": "Require EvidenceGate validation and retry evidence collection.",
        "severity": "Medium",
    },
    "Unsupported root cause": {
        "description": "Agent introduces a root-cause claim that is not supported by logs or evidence.",
        "recommended_control": "Block action until evidence supports the claim.",
        "severity": "High",
    },
    "Instruction contamination": {
        "description": "Unsafe or injected instruction enters the agent workflow.",
        "recommended_control": "Quarantine injected instruction and prevent downstream reuse.",
        "severity": "Critical",
    },
    "Incorrect verification": {
        "description": "Verifier declares success without checking hard evidence or tool output.",
        "recommended_control": "Externalize verification and require health-check/tool evidence.",
        "severity": "High",
    },
    "Unsafe delegation": {
        "description": "Agent attempts an action outside its role, policy, or permission scope.",
        "recommended_control": "Apply least-privilege permissions and policy enforcement.",
        "severity": "Critical",
    },
    "Premature action": {
        "description": "Agent recommends or executes action before enough evidence is available.",
        "recommended_control": "Require clarification, verification, or human approval.",
        "severity": "High",
    },
    "Propagation effect": {
        "description": "Downstream agents reuse risky context from an earlier faulty step.",
        "recommended_control": "Trace provenance and isolate contaminated context.",
        "severity": "High",
    },
}


def build_trace(scenario: str) -> pd.DataFrame:
    return pd.DataFrame(
        SCENARIOS[scenario]["trace"],
        columns=[
            "step",
            "agent",
            "event",
            "evidence_source",
            "trace_label",
            "trace_indicator",
            "status",
        ],
    )


def classify_row(row: pd.Series):
    event = str(row["event"]).lower()
    evidence = str(row["evidence_source"]).lower()
    trace_label = str(row["trace_label"]).lower()
    status = str(row["status"]).lower()
    risk = float(row["trace_indicator"])

    if "injected instruction" in evidence or "ignore verification" in event:
        return "Instruction contamination", 0.96, "Critical", TAXONOMY["Instruction contamination"]["recommended_control"]

    if "permission" in event or "outside allowed permission" in event:
        return "Unsafe delegation", 0.94, "Critical", TAXONOMY["Unsafe delegation"]["recommended_control"]

    if "declared success" in event or "missing verification" in evidence:
        return "Incorrect verification", 0.90, "High", TAXONOMY["Incorrect verification"]["recommended_control"]

    if "invented" in event or "unsupported claim" in event or "weak memory" in evidence:
        return "Unsupported root cause", 0.88, "High", TAXONOMY["Unsupported root cause"]["recommended_control"]

    if "missing" in event or "timed out" in event or "missing tool output" in evidence:
        return "Missing evidence", 0.86, "Medium", TAXONOMY["Missing evidence"]["recommended_control"]

    if "premature" in trace_label or "suggested remediation despite incomplete evidence" in event:
        return "Premature action", 0.84, "High", TAXONOMY["Premature action"]["recommended_control"]

    if "propagated" in trace_label or "contaminated" in evidence:
        return "Propagation effect", 0.82, "High", TAXONOMY["Propagation effect"]["recommended_control"]

    if risk < 0.30 and status in ["passed", "needs review"]:
        return "No failure", 0.78, "Low", TAXONOMY["No failure"]["recommended_control"]

    if status in ["blocked", "contained", "escalated"]:
        return "Propagation effect", 0.76, "High", TAXONOMY["Propagation effect"]["recommended_control"]

    return "No failure", 0.65, "Low", TAXONOMY["No failure"]["recommended_control"]


def classify_trace(df: pd.DataFrame, sensitivity: str) -> pd.DataFrame:
    classified_rows = []

    for _, row in df.iterrows():
        category, confidence, severity, control = classify_row(row)

        if sensitivity == "Strict":
            if row["trace_indicator"] >= 0.50 and category == "No failure":
                category = "Propagation effect"
                confidence = 0.70
                severity = "Medium"
                control = TAXONOMY["Propagation effect"]["recommended_control"]

        elif sensitivity == "High recall":
            if row["trace_indicator"] >= 0.35 and category == "No failure":
                category = "Propagation effect"
                confidence = 0.68
                severity = "Medium"
                control = TAXONOMY["Propagation effect"]["recommended_control"]

        classified_rows.append(
            {
                "step": row["step"],
                "agent": row["agent"],
                "event": row["event"],
                "trace_indicator": row["trace_indicator"],
                "status": row["status"],
                "failure_category": category,
                "severity": severity,
                "rule_score": round(confidence, 2),
                "recommended_control": control,
            }
        )

    return pd.DataFrame(classified_rows)


def get_primary_failure(classified_df: pd.DataFrame) -> str:
    non_clean = classified_df[classified_df["failure_category"] != "No failure"]

    if non_clean.empty:
        return "No failure"

    severity_rank = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4,
    }

    non_clean = non_clean.copy()
    non_clean["severity_rank"] = non_clean["severity"].map(severity_rank)

    top = non_clean.sort_values(
        by=["severity_rank", "rule_score", "trace_indicator"],
        ascending=False,
    ).iloc[0]

    return str(top["failure_category"])


def build_svg_path():
    commands = []

    for idx, agent in enumerate(AGENTS):
        x, y = SVG_POSITIONS[agent]
        if idx == 0:
            commands.append(f"M {x} {y}")
        else:
            commands.append(f"L {x} {y}")

    return " ".join(commands)


def build_mast_replay_html(classified_df: pd.DataFrame, scenario: str, primary_failure: str, animate: bool):
    motion_path = build_svg_path()
    duration = 4.8

    edge_lines = []

    for source, target in EDGES:
        x1, y1 = SVG_POSITIONS[source]
        x2, y2 = SVG_POSITIONS[target]
        edge_lines.append(
            f"""
            <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
                  stroke="rgba(148,163,184,0.40)" stroke-width="3" />
            """
        )

    node_items = []

    for idx, agent in enumerate(AGENTS):
        x, y = SVG_POSITIONS[agent]
        row = classified_df.loc[classified_df["agent"] == agent].iloc[0]
        severity = row["severity"]
        category = row["failure_category"]

        final_color = SEVERITY_COLORS.get(severity, "#94a3b8")
        begin_time = idx * 0.55

        safe_agent = html.escape(agent)
        safe_category = html.escape(category)

        if animate:
            circle = f"""
                <circle cx="{x}" cy="{y}" r="19"
                        fill="{SEVERITY_COLORS['pending']}"
                        stroke="rgba(248,250,252,0.85)"
                        stroke-width="3">
                    <animate attributeName="fill"
                             from="{SEVERITY_COLORS['pending']}"
                             to="{final_color}"
                             begin="{begin_time}s"
                             dur="0.22s"
                             fill="freeze" />
                </circle>
            """
            pulse = f"""
                <circle cx="{x}" cy="{y}" r="25"
                        fill="none"
                        stroke="{final_color}"
                        stroke-width="2"
                        opacity="0">
                    <animate attributeName="opacity"
                             values="0;0.85;0"
                             begin="{begin_time}s"
                             dur="0.65s"
                             fill="freeze" />
                    <animate attributeName="r"
                             values="21;31;25"
                             begin="{begin_time}s"
                             dur="0.65s"
                             fill="freeze" />
                </circle>
            """
        else:
            circle = f"""
                <circle cx="{x}" cy="{y}" r="19"
                        fill="{final_color}"
                        stroke="rgba(248,250,252,0.85)"
                        stroke-width="3" />
            """
            pulse = ""

        node_items.append(
            f"""
            <g>
                {circle}
                {pulse}
                <text x="{x}" y="{y + 43}"
                      text-anchor="middle"
                      fill="#e5e7eb"
                      font-size="13"
                      font-weight="600">{safe_agent}</text>
                <text x="{x}" y="{y + 60}"
                      text-anchor="middle"
                      fill="#94a3b8"
                      font-size="10">{safe_category}</text>
            </g>
            """
        )

    if animate:
        runner_path = f"""
            <path d="{motion_path}"
                  fill="none"
                  stroke="rgba(56,189,248,0.95)"
                  stroke-width="5"
                  stroke-linecap="round"
                  stroke-dasharray="1200"
                  stroke-dashoffset="1200">
                <animate attributeName="stroke-dashoffset"
                         from="1200"
                         to="0"
                         dur="{duration}s"
                         fill="freeze" />
            </path>

            <circle r="10" fill="#ffffff" stroke="#38bdf8" stroke-width="5" class="runner">
                <animateMotion dur="{duration}s"
                               path="{motion_path}"
                               fill="freeze"
                               calcMode="linear" />
            </circle>
        """
    else:
        runner_path = f"""
            <path d="{motion_path}"
                  fill="none"
                  stroke="rgba(56,189,248,0.95)"
                  stroke-width="5"
                  stroke-linecap="round" />
            <circle cx="{SVG_POSITIONS['Report Agent'][0]}"
                    cy="{SVG_POSITIONS['Report Agent'][1]}"
                    r="10"
                    fill="#ffffff"
                    stroke="#38bdf8"
                    stroke-width="5"
                    class="runner" />
        """

    html_code = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                background: transparent;
                font-family: Segoe UI, Arial, sans-serif;
            }}
            .graph-card {{
                width: 100%;
                border-radius: 20px;
                background: rgba(15, 23, 42, 0.55);
                border: 1px solid rgba(148, 163, 184, 0.18);
                padding: 12px;
                box-sizing: border-box;
            }}
            .title-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: #e5e7eb;
                padding: 0 10px 4px 10px;
            }}
            .title {{
                font-size: 14px;
                font-weight: 700;
            }}
            .status {{
                font-size: 12px;
                color: #94a3b8;
            }}
            .runner {{
                filter: drop-shadow(0 0 8px rgba(56,189,248,0.85));
            }}
        </style>
    </head>

    <body>
        <div class="graph-card">
            <div class="title-row">
                <div class="title">MAST classification replay</div>
                <div class="status">Scenario: {html.escape(scenario)} | Primary: {html.escape(primary_failure)}</div>
            </div>

            <svg viewBox="0 0 900 330" width="100%" height="390">
                {"".join(edge_lines)}
                {runner_path}
                {"".join(node_items)}
            </svg>
        </div>
    </body>
    </html>
    """

    return html_code


def build_category_chart(classified_df: pd.DataFrame):
    counts = classified_df["failure_category"].value_counts().reset_index()
    counts.columns = ["failure_category", "count"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=counts["failure_category"],
            y=counts["count"],
            text=counts["count"],
            textposition="outside",
            hovertemplate="Category: %{x}<br>Count: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        height=330,
        margin=dict(l=20, r=20, t=30, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Failure category", gridcolor="rgba(148,163,184,0.15)"),
        yaxis=dict(title="Count", gridcolor="rgba(148,163,184,0.15)", dtick=1),
    )

    return fig


def build_severity_chart(classified_df: pd.DataFrame):
    severity_order = ["Low", "Medium", "High", "Critical"]
    counts = classified_df["severity"].value_counts().reindex(severity_order).fillna(0).reset_index()
    counts.columns = ["severity", "count"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=counts["severity"],
            y=counts["count"],
            text=counts["count"],
            textposition="outside",
            hovertemplate="Severity: %{x}<br>Count: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        height=330,
        margin=dict(l=20, r=20, t=30, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Severity", gridcolor="rgba(148,163,184,0.15)"),
        yaxis=dict(title="Count", gridcolor="rgba(148,163,184,0.15)", dtick=1),
    )

    return fig


def build_taxonomy_table() -> pd.DataFrame:
    rows = []

    for category, details in TAXONOMY.items():
        rows.append(
            {
                "failure_category": category,
                "severity": details["severity"],
                "description": details["description"],
                "recommended_control": details["recommended_control"],
            }
        )

    return pd.DataFrame(rows)


page_header(
    "MAST Classifier",
    "A project-local deterministic rule-based failure taxonomy demonstrator. It classifies illustrative synthetic traces; it is not a trained model and its rule scores are not calibrated probabilities.",
)

scenario_options = list(SCENARIOS.keys())
sensitivity_options = ["Balanced", "Strict", "High recall"]

if "mast_scenario" not in st.session_state:
    st.session_state.mast_scenario = "Hallucinated root cause"

if "mast_sensitivity" not in st.session_state:
    st.session_state.mast_sensitivity = "Balanced"

if "mast_animate_now" not in st.session_state:
    st.session_state.mast_animate_now = False

left, right = st.columns([1, 1.7])

with left:
    st.markdown("### Rule controls")

    selected_scenario = st.selectbox(
        "Select trace scenario",
        scenario_options,
        index=scenario_options.index(st.session_state.mast_scenario),
    )

    selected_sensitivity = st.selectbox(
        "Rule sensitivity",
        sensitivity_options,
        index=sensitivity_options.index(st.session_state.mast_sensitivity),
    )

    if st.button("Run MAST classification", use_container_width=True):
        st.session_state.mast_scenario = selected_scenario
        st.session_state.mast_sensitivity = selected_sensitivity
        st.session_state.mast_animate_now = True
        st.rerun()

scenario = st.session_state.mast_scenario
sensitivity = st.session_state.mast_sensitivity

trace_df = build_trace(scenario)
classified_df = classify_trace(trace_df, sensitivity)

primary_failure = get_primary_failure(classified_df)
critical_count = int((classified_df["severity"] == "Critical").sum())
high_count = int((classified_df["severity"] == "High").sum())
classified_failures = int((classified_df["failure_category"] != "No failure").sum())
avg_rule_score = round(classified_df["rule_score"].mean(), 2)

with left:
    st.markdown(
        f"""
        <div class="module-card">
            <h3>Active classification</h3>
            <p><b>Scenario:</b> {scenario}</p>
            <p><b>Sensitivity:</b> {sensitivity}</p>
            <p><b>Trace description:</b> {SCENARIOS[scenario]["description"]}</p>
            <span class="tag">taxonomy</span>
            <span class="tag">failure classification</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown("### Classification replay")
    components.html(
        build_mast_replay_html(
            classified_df=classified_df,
            scenario=scenario,
            primary_failure=primary_failure,
            animate=st.session_state.mast_animate_now,
        ),
        height=430,
        scrolling=False,
    )

    st.markdown("### Rule-based result")
    st.markdown(
        f"""
        <div class="module-card">
            <h3>{primary_failure}</h3>
            <p>
            The deterministic rules inspect each illustrative trace step for evidence quality, unsafe instructions, unsupported claims,
            verification failures, premature actions, propagation effects, and permission violations.
            </p>
            <p><b>Primary recommended control:</b> {TAXONOMY[primary_failure]["recommended_control"]}</p>
            <span class="tag">rule-based baseline</span>
            <span class="tag">explainable classification</span>
            <span class="tag">control mapping</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.mast_animate_now:
    st.session_state.mast_animate_now = False

st.success(f"Active run: {scenario}. Primary failure category: {primary_failure}.")

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Primary failure", primary_failure, "Highest-priority rule label")

with m2:
    metric_card("Classified failures", str(classified_failures), "Steps not labelled as clean")

with m3:
    metric_card("Critical/High steps", f"{critical_count}/{high_count}", "Critical and high severity counts")

with m4:
    metric_card("Avg rule score", str(avg_rule_score), "Deterministic heuristic; not confidence")

st.divider()

chart_col, severity_col = st.columns([1.3, 1])

with chart_col:
    section(
        "Failure category distribution",
        "Counts of taxonomy categories assigned to the trace steps.",
    )
    st.plotly_chart(
        build_category_chart(classified_df),
        use_container_width=True,
        config={"displayModeBar": False},
    )

with severity_col:
    section(
        "Severity distribution",
        "Counts of low, medium, high, and critical labels.",
    )
    st.plotly_chart(
        build_severity_chart(classified_df),
        use_container_width=True,
        config={"displayModeBar": False},
    )

st.divider()

section(
    "Classified trace",
    "Each row shows the illustrative synthetic event plus the rule-assigned category, severity, heuristic rule score, and recommended control.",
)

st.dataframe(
    classified_df,
    use_container_width=True,
    hide_index=True,
    height=360,
)

st.divider()

section(
    "Original trace",
    "Illustrative synthetic trace used by the deterministic rules before taxonomy labels are applied.",
)

st.dataframe(
    trace_df,
    use_container_width=True,
    hide_index=True,
    height=260,
)

st.divider()

section(
    "Taxonomy reference",
    "This project-local taxonomy maps illustrative synthetic events to deterministic failure labels and suggested controls.",
)

st.dataframe(
    build_taxonomy_table(),
    use_container_width=True,
    hide_index=True,
    height=320,
)

st.divider()

section(
    "Engineering interpretation",
    "The MAST view is a rule-based diagnostic demonstrator. It assigns predefined labels, severity categories, heuristic rule scores, and suggested controls to illustrative synthetic traces. It is not a trained classifier or empirical validation of the taxonomy.",
)

st.divider()

section(
    "Claim boundary",
    (
        "MAST is a project-local label for this deterministic "
        "rule-based taxonomy demonstrator. It is not presented "
        "as an external standard, validated safety taxonomy, "
        "trained machine-learning model, or calibrated classifier."
    ),
)
