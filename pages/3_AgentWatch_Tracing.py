import html

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

from src.ui import apply_global_style, page_header, metric_card, section

st.set_page_config(
    page_title="AgentWatch Tracing",
    page_icon="🔎",
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

STATUS_COLORS = {
    "passed": "#38bdf8",
    "needs review": "#facc15",
    "warning": "#f97316",
    "high risk": "#ef4444",
    "blocked": "#facc15",
    "contained": "#22c55e",
    "escalated": "#f97316",
    "unsafe": "#ef4444",
    "pending": "#475569",
}


SCENARIOS = {
    "Normal workflow": {
        "root_cause": "None",
        "failure_class": "No failure",
        "containment": "Not required",
        "diagnosis": "The workflow completed with verified evidence and no downstream contamination.",
    },
    "Hallucinated root cause": {
        "root_cause": "Knowledge Agent",
        "failure_class": "Unsupported root-cause propagation",
        "containment": "Blocked at Verification Agent",
        "diagnosis": "The Knowledge Agent introduced an unsupported database-saturation claim. The Action Agent reused it before EvidenceGate blocked the recommendation.",
    },
    "Missing evidence": {
        "root_cause": "Log Analysis Agent",
        "failure_class": "Missing evidence / weak support",
        "containment": "Escalated by Safety Agent",
        "diagnosis": "The Log Analysis Agent failed to retrieve required logs. Downstream agents used generic runbook knowledge without incident-specific evidence.",
    },
    "Prompt injection attempt": {
        "root_cause": "Action Agent",
        "failure_class": "Instruction contamination",
        "containment": "Quarantined by Safety Agent",
        "diagnosis": "The Action Agent received an unsafe instruction to ignore verification and close the incident. The instruction was blocked and quarantined.",
    },
}


def build_trace(scenario: str) -> pd.DataFrame:
    if scenario == "Normal workflow":
        rows = [
            [1, "User Report", "external_alert", "Payment API outage reported", "alert payload", "received", 0.08, "passed", False],
            [2, "Triage Agent", "User Report", "Classified incident as P2 payment API outage", "alert metadata", "classification", 0.12, "passed", False],
            [3, "Log Analysis Agent", "Triage Agent", "Found repeated 503 errors in logs", "log query", "evidence_found", 0.16, "passed", False],
            [4, "Knowledge Agent", "Log Analysis Agent", "Matched gateway timeout runbook", "runbook KB-104", "retrieved", 0.18, "passed", False],
            [5, "Action Agent", "Knowledge Agent", "Recommended connector pool restart", "logs + runbook", "recommended", 0.22, "needs review", False],
            [6, "Verification Agent", "Action Agent", "Verified remediation evidence", "EvidenceGate", "verified", 0.10, "passed", False],
            [7, "Safety Agent", "Verification Agent", "Approved action within policy scope", "policy check", "approved", 0.07, "passed", False],
            [8, "Report Agent", "Safety Agent", "Generated final incident summary", "trace records", "reported", 0.05, "passed", False],
        ]

    elif scenario == "Hallucinated root cause":
        rows = [
            [1, "User Report", "external_alert", "Payment API outage reported", "alert payload", "received", 0.10, "passed", False],
            [2, "Triage Agent", "User Report", "Classified incident as P2 payment API outage", "alert metadata", "classification", 0.16, "passed", False],
            [3, "Log Analysis Agent", "Triage Agent", "No database failure found in logs", "log query", "evidence_found", 0.24, "passed", False],
            [4, "Knowledge Agent", "Log Analysis Agent", "Invented database saturation without log evidence", "weak memory match", "fault_seed", 0.82, "warning", True],
            [5, "Action Agent", "Knowledge Agent", "Recommended database restart from unsupported claim", "contaminated context", "propagated", 0.92, "high risk", False],
            [6, "Verification Agent", "Action Agent", "Blocked action due to missing database evidence", "EvidenceGate", "blocked", 0.88, "blocked", False],
            [7, "Safety Agent", "Verification Agent", "Quarantined unsupported database claim", "policy check", "contained", 0.35, "contained", False],
            [8, "Report Agent", "Safety Agent", "Reported blocked hallucinated root-cause path", "trace records", "reported", 0.20, "passed", False],
        ]

    elif scenario == "Missing evidence":
        rows = [
            [1, "User Report", "external_alert", "Payment API outage reported", "alert payload", "received", 0.10, "passed", False],
            [2, "Triage Agent", "User Report", "Classified incident as P2 payment API outage", "alert metadata", "classification", 0.18, "passed", False],
            [3, "Log Analysis Agent", "Triage Agent", "Log query timed out; required evidence missing", "missing tool output", "fault_seed", 0.74, "warning", True],
            [4, "Knowledge Agent", "Log Analysis Agent", "Retrieved generic gateway runbook without incident proof", "generic runbook", "weak_support", 0.68, "warning", False],
            [5, "Action Agent", "Knowledge Agent", "Suggested remediation despite incomplete evidence", "weak context", "premature_action", 0.76, "high risk", False],
            [6, "Verification Agent", "Action Agent", "Rejected completion because logs were missing", "EvidenceGate", "blocked", 0.70, "blocked", False],
            [7, "Safety Agent", "Verification Agent", "Escalated to human review and requested log retry", "policy check", "escalated", 0.58, "escalated", False],
            [8, "Report Agent", "Safety Agent", "Generated incomplete-evidence escalation summary", "trace records", "reported", 0.42, "passed", False],
        ]

    else:
        rows = [
            [1, "User Report", "external_alert", "Payment API outage reported", "alert payload", "received", 0.10, "passed", False],
            [2, "Triage Agent", "User Report", "Classified incident as P2 payment API outage", "alert metadata", "classification", 0.14, "passed", False],
            [3, "Log Analysis Agent", "Triage Agent", "Found 503 errors in payment-api logs", "log query", "evidence_found", 0.18, "passed", False],
            [4, "Knowledge Agent", "Log Analysis Agent", "Retrieved gateway timeout runbook", "runbook KB-104", "retrieved", 0.22, "passed", False],
            [5, "Action Agent", "Knowledge Agent", "Received instruction to ignore verification and close incident", "injected instruction", "fault_seed", 0.98, "unsafe", True],
            [6, "Verification Agent", "Action Agent", "Detected unsupported instruction and refused closure", "EvidenceGate", "blocked", 0.96, "blocked", False],
            [7, "Safety Agent", "Verification Agent", "Quarantined injected instruction from downstream context", "policy check", "contained", 0.30, "contained", False],
            [8, "Report Agent", "Safety Agent", "Generated safe report with injection warning", "trace records", "reported", 0.16, "passed", False],
        ]

    return pd.DataFrame(
        rows,
        columns=[
            "step",
            "agent",
            "input_source",
            "event",
            "evidence_source",
            "trace_label",
            "risk_score",
            "status",
            "root_cause",
        ],
    )


def build_svg_path():
    commands = []

    for idx, agent in enumerate(AGENTS):
        x, y = SVG_POSITIONS[agent]

        if idx == 0:
            commands.append(f"M {x} {y}")
        else:
            commands.append(f"L {x} {y}")

    return " ".join(commands)


def build_agentwatch_replay_html(df: pd.DataFrame, scenario: str, animate: bool):
    motion_path = build_svg_path()
    duration = 4.8

    root_rows = df[df["root_cause"] == True]
    if root_rows.empty:
        root_cause_agent = "None"
    else:
        root_cause_agent = root_rows.iloc[0]["agent"]

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
        row = df.loc[df["agent"] == agent].iloc[0]
        status = row["status"]
        is_root = bool(row["root_cause"])

        if is_root:
            final_color = "#ef4444"
            label = "root cause"
        else:
            final_color = STATUS_COLORS.get(status, "#94a3b8")
            label = status

        begin_time = idx * 0.55
        safe_agent = html.escape(agent)
        safe_label = html.escape(label)

        if animate:
            circle_fill = f"""
                <circle cx="{x}" cy="{y}" r="19"
                        fill="{STATUS_COLORS['pending']}"
                        stroke="rgba(248,250,252,0.85)"
                        stroke-width="3">
                    <animate attributeName="fill"
                             from="{STATUS_COLORS['pending']}"
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
            circle_fill = f"""
                <circle cx="{x}" cy="{y}" r="19"
                        fill="{final_color}"
                        stroke="rgba(248,250,252,0.85)"
                        stroke-width="3" />
            """

            pulse = ""

        node_items.append(
            f"""
            <g>
                {circle_fill}
                {pulse}

                <text x="{x}" y="{y + 43}"
                      text-anchor="middle"
                      fill="#e5e7eb"
                      font-size="13"
                      font-weight="600">{safe_agent}</text>

                <text x="{x}" y="{y + 60}"
                      text-anchor="middle"
                      fill="#94a3b8"
                      font-size="11">{safe_label}</text>
            </g>
            """
        )

    if animate:
        animated_path = f"""
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
        animated_path = f"""
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
                <div class="title">AgentWatch trace replay</div>
                <div class="status">Scenario: {html.escape(scenario)} | Root cause: {html.escape(root_cause_agent)}</div>
            </div>

            <svg viewBox="0 0 900 330" width="100%" height="390">
                {"".join(edge_lines)}
                {animated_path}
                {"".join(node_items)}
            </svg>
        </div>
    </body>
    </html>
    """

    return html_code


def build_timeline(df: pd.DataFrame):
    colors = [STATUS_COLORS.get(status, "#94a3b8") for status in df["status"]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["step"],
            y=df["risk_score"],
            mode="lines+markers+text",
            text=df["agent"],
            textposition="top center",
            marker=dict(
                size=14,
                color=colors,
                line=dict(width=2, color="#e5e7eb"),
            ),
            line=dict(width=3),
            hovertemplate="<b>%{text}</b><br>Step %{x}<br>Risk: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        height=390,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Trace step", gridcolor="rgba(148,163,184,0.15)", dtick=1),
        yaxis=dict(title="Risk score", range=[0, 1], gridcolor="rgba(148,163,184,0.15)"),
    )

    return fig


def build_failure_focus(df: pd.DataFrame):
    return df[
        (df["risk_score"] >= 0.50)
        | (df["root_cause"] == True)
        | (df["status"].isin(["blocked", "contained", "escalated", "unsafe", "high risk"]))
    ].copy()


def render_provenance_cards(df: pd.DataFrame):
    for i in range(0, len(df), 4):
        chunk = df.iloc[i:i + 4]
        cols = st.columns(len(chunk))

        for col, (_, row) in zip(cols, chunk.iterrows()):
            with col:
                if row["root_cause"]:
                    tag_class = "danger-tag"
                    tag_text = "ROOT CAUSE"
                elif row["status"] in ["blocked", "contained", "escalated"]:
                    tag_class = "warning-tag"
                    tag_text = row["status"]
                else:
                    tag_class = "tag"
                    tag_text = row["trace_label"]

                st.markdown(
                    f"""
                    <div class="module-card" style="min-height:155px;">
                        <h3>{row["step"]}. {row["agent"]}</h3>
                        <p><b>Input:</b> {row["input_source"]}</p>
                        <p><b>Risk:</b> {row["risk_score"]}</p>
                        <span class="{tag_class}">{tag_text}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


page_header(
    "AgentWatch Tracing",
    "Step-level observability for multi-agent workflows. This module records agent handoffs, evidence sources, risk scores, root-cause candidates, and containment actions.",
)

scenario_options = list(SCENARIOS.keys())

if "trace_scenario" not in st.session_state:
    st.session_state.trace_scenario = "Hallucinated root cause"

if "trace_animate_now" not in st.session_state:
    st.session_state.trace_animate_now = False

left, right = st.columns([1, 1.7])

with left:
    st.markdown("### Trace control")

    selected_scenario = st.selectbox(
        "Select trace scenario",
        scenario_options,
        index=scenario_options.index(st.session_state.trace_scenario),
    )

    if st.button("Run trace analysis", use_container_width=True):
        st.session_state.trace_scenario = selected_scenario
        st.session_state.trace_animate_now = True
        st.rerun()

scenario = st.session_state.trace_scenario
df = build_trace(scenario)
summary = SCENARIOS[scenario]
failure_focus = build_failure_focus(df)

root_cause_agent = summary["root_cause"]
max_risk = round(df["risk_score"].max(), 2)
high_risk_steps = int((df["risk_score"] >= 0.70).sum())

with left:
    st.markdown(
        f"""
        <div class="module-card">
            <h3>Active trace</h3>
            <p><b>Scenario:</b> {scenario}</p>
            <p><b>Failure class:</b> {summary["failure_class"]}</p>
            <p><b>Root cause:</b> {root_cause_agent}</p>
            <span class="tag">observability</span>
            <span class="tag">root cause</span>
            <span class="tag">provenance</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown("### Trace replay")
    components.html(
        build_agentwatch_replay_html(
            df=df,
            scenario=scenario,
            animate=st.session_state.trace_animate_now,
        ),
        height=430,
        scrolling=False,
    )

    st.markdown("### Diagnosis")
    st.markdown(
        f"""
        <div class="module-card">
            <h3>{summary["failure_class"]}</h3>
            <p>{summary["diagnosis"]}</p>
            <p><b>Containment:</b> {summary["containment"]}</p>
            <span class="tag">trace diagnosis</span>
            <span class="tag">evidence chain</span>
            <span class="tag">containment analysis</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.trace_animate_now:
    st.session_state.trace_animate_now = False

st.success(f"Active trace: {scenario}. Root-cause candidate: {root_cause_agent}.")

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Root cause agent", root_cause_agent, "First abnormal high-impact step")

with m2:
    metric_card("Max risk", str(max_risk), "Highest trace risk score")

with m3:
    metric_card("High-risk steps", str(high_risk_steps), "Steps with risk score ≥ 0.70")

with m4:
    metric_card("Containment", summary["containment"], "Block, escalate, quarantine, or approve")

st.divider()

section(
    "Trace timeline",
    "The timeline shows how risk changes across the agent workflow and where the root cause appears.",
)

st.plotly_chart(
    build_timeline(df),
    use_container_width=True,
    config={"displayModeBar": False},
)

st.divider()

section(
    "Failure-focused trace",
    "This table filters the trace to the steps that matter most for diagnosis: root cause, high-risk events, blocked actions, containment, and escalation.",
)

st.dataframe(
    failure_focus,
    use_container_width=True,
    hide_index=True,
    height=260,
)

st.divider()

section(
    "Full execution trace",
    "The full trace records each agent, input source, event, evidence source, trace label, risk score, and status.",
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=330,
)

st.divider()

section(
    "Provenance view",
    "Each card shows how information moved from one agent to the next. The root-cause step is marked separately from downstream effects.",
)

render_provenance_cards(df)

st.divider()

section(
    "Engineering interpretation",
    "AgentWatch turns a multi-agent workflow into an auditable trace. Instead of only seeing the final answer, the system exposes which agent produced which claim, what evidence supported it, where the risk increased, and where containment happened. This is the observability layer required before agentic systems can be treated as serious enterprise workflows.",
)