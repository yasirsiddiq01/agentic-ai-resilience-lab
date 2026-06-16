import html

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

from src.ui import apply_global_style, page_header, metric_card, section

st.set_page_config(
    page_title="Enterprise Incident Workflow",
    page_icon="🏢",
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
    "pending": "#475569",
    "normal": "#38bdf8",
    "evidence": "#22c55e",
    "warning": "#f97316",
    "fault seed": "#ef4444",
    "blocked": "#facc15",
    "contained": "#22c55e",
    "escalated": "#f97316",
    "reported": "#38bdf8",
}


SCENARIOS = {
    "Normal workflow": {
        "objective": "Resolve a payment API incident using verified logs, runbook evidence, policy checks, and final reporting.",
        "summary": "The workflow completes normally. Evidence is collected, the action is verified, and the final report is generated.",
        "root_cause": "None",
        "containment": "Not required",
    },
    "Hallucinated root cause": {
        "objective": "Test whether an unsupported database-saturation claim is detected before it becomes an operational action.",
        "summary": "The Knowledge Agent introduces an unsupported root cause. The Action Agent reuses it, but Verification blocks the action.",
        "root_cause": "Knowledge Agent",
        "containment": "Verification Agent",
    },
    "Missing evidence": {
        "objective": "Test whether the workflow can detect that required logs are missing before recommending remediation.",
        "summary": "The Log Analysis Agent cannot retrieve required logs. The workflow escalates instead of closing the incident.",
        "root_cause": "Log Analysis Agent",
        "containment": "Safety Agent",
    },
    "Prompt injection attempt": {
        "objective": "Test whether an unsafe instruction to ignore verification is blocked and quarantined.",
        "summary": "The Action Agent receives an unsafe instruction. Verification blocks closure and Safety quarantines the injected context.",
        "root_cause": "Action Agent",
        "containment": "Safety Agent",
    },
}


def build_trace(scenario: str) -> pd.DataFrame:
    if scenario == "Normal workflow":
        rows = [
            [1, "User Report", "Payment API outage reported by monitoring alert.", "normal", 0.08],
            [2, "Triage Agent", "Classified incident as P2 payment API outage.", "normal", 0.12],
            [3, "Log Analysis Agent", "Found repeated 503 errors in payment-api logs.", "evidence", 0.16],
            [4, "Knowledge Agent", "Retrieved gateway timeout runbook.", "evidence", 0.18],
            [5, "Action Agent", "Recommended connector pool restart.", "normal", 0.22],
            [6, "Verification Agent", "Verified recommendation against logs and runbook.", "evidence", 0.10],
            [7, "Safety Agent", "Approved action within policy scope.", "evidence", 0.07],
            [8, "Report Agent", "Generated final incident summary.", "reported", 0.05],
        ]

    elif scenario == "Hallucinated root cause":
        rows = [
            [1, "User Report", "Payment API outage reported by monitoring alert.", "normal", 0.10],
            [2, "Triage Agent", "Classified incident as P2 payment API outage.", "normal", 0.16],
            [3, "Log Analysis Agent", "No database failure found in logs.", "evidence", 0.24],
            [4, "Knowledge Agent", "Invented database saturation without log evidence.", "fault seed", 0.82],
            [5, "Action Agent", "Recommended database restart from unsupported claim.", "warning", 0.92],
            [6, "Verification Agent", "Blocked action due to missing database evidence.", "blocked", 0.88],
            [7, "Safety Agent", "Quarantined unsupported database claim.", "contained", 0.35],
            [8, "Report Agent", "Reported blocked hallucinated root-cause path.", "reported", 0.20],
        ]

    elif scenario == "Missing evidence":
        rows = [
            [1, "User Report", "Payment API outage reported by monitoring alert.", "normal", 0.10],
            [2, "Triage Agent", "Classified incident as P2 payment API outage.", "normal", 0.18],
            [3, "Log Analysis Agent", "Log query timed out; required evidence missing.", "fault seed", 0.74],
            [4, "Knowledge Agent", "Retrieved generic gateway runbook without incident-specific proof.", "warning", 0.68],
            [5, "Action Agent", "Suggested remediation despite incomplete evidence.", "warning", 0.76],
            [6, "Verification Agent", "Rejected completion because logs were missing.", "blocked", 0.70],
            [7, "Safety Agent", "Escalated to human review and requested log retry.", "escalated", 0.58],
            [8, "Report Agent", "Generated incomplete-evidence escalation summary.", "reported", 0.42],
        ]

    else:
        rows = [
            [1, "User Report", "Payment API outage reported by monitoring alert.", "normal", 0.10],
            [2, "Triage Agent", "Classified incident as P2 payment API outage.", "normal", 0.14],
            [3, "Log Analysis Agent", "Found 503 errors in payment-api logs.", "evidence", 0.18],
            [4, "Knowledge Agent", "Retrieved gateway timeout runbook.", "evidence", 0.22],
            [5, "Action Agent", "Received instruction to ignore verification and close incident.", "fault seed", 0.98],
            [6, "Verification Agent", "Detected unsupported instruction and refused closure.", "blocked", 0.96],
            [7, "Safety Agent", "Quarantined injected instruction.", "contained", 0.30],
            [8, "Report Agent", "Generated safe report with injection warning.", "reported", 0.16],
        ]

    return pd.DataFrame(
        rows,
        columns=["step", "agent", "event", "status", "risk_score"],
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


def build_workflow_replay_html(df: pd.DataFrame, scenario: str, animate: bool):
    motion_path = build_svg_path()
    duration = 4.8
    summary = SCENARIOS[scenario]

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
        final_color = STATUS_COLORS.get(status, "#94a3b8")
        begin_time = idx * 0.55

        safe_agent = html.escape(agent)
        safe_status = html.escape(status)

        if animate:
            circle = f"""
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
                      font-size="11">{safe_status}</text>
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
                <div class="title">Enterprise incident replay</div>
                <div class="status">Scenario: {html.escape(scenario)} | Containment: {html.escape(summary["containment"])}</div>
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


def build_risk_chart(df: pd.DataFrame):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["step"],
            y=df["risk_score"],
            mode="lines+markers+text",
            text=df["agent"],
            textposition="top center",
            line=dict(width=3),
            marker=dict(size=10),
            hovertemplate="<b>%{text}</b><br>Step %{x}<br>Risk: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        height=340,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Workflow step", gridcolor="rgba(148,163,184,0.15)", dtick=1),
        yaxis=dict(title="Risk score", range=[0, 1], gridcolor="rgba(148,163,184,0.15)"),
    )

    return fig


def build_comparison_table():
    rows = []

    for scenario in SCENARIOS.keys():
        trace = build_trace(scenario)
        rows.append(
            {
                "scenario": scenario,
                "root_cause": SCENARIOS[scenario]["root_cause"],
                "containment": SCENARIOS[scenario]["containment"],
                "max_risk": round(trace["risk_score"].max(), 2),
                "high_risk_steps": int((trace["risk_score"] >= 0.70).sum()),
            }
        )

    return pd.DataFrame(rows)


page_header(
    "Enterprise Incident Workflow",
    "A realistic enterprise-style incident resolution workflow with agent handoffs, evidence checks, safety controls, and final reporting.",
)

scenario_options = list(SCENARIOS.keys())

if "workflow_scenario" not in st.session_state:
    st.session_state.workflow_scenario = "Normal workflow"

if "workflow_animate_now" not in st.session_state:
    st.session_state.workflow_animate_now = False

left, right = st.columns([1, 1.7])

with left:
    st.markdown("### Scenario control")

    selected_scenario = st.selectbox(
        "Select workflow condition",
        scenario_options,
        index=scenario_options.index(st.session_state.workflow_scenario),
    )

    if st.button("Run incident workflow", use_container_width=True):
        st.session_state.workflow_scenario = selected_scenario
        st.session_state.workflow_animate_now = True
        st.rerun()

scenario = st.session_state.workflow_scenario
df = build_trace(scenario)
summary = SCENARIOS[scenario]

max_risk = round(df["risk_score"].max(), 2)
high_risk_steps = int((df["risk_score"] >= 0.70).sum())

with left:
    st.markdown(
        f"""
        <div class="module-card">
            <h3>Active experiment</h3>
            <p><b>Scenario:</b> {scenario}</p>
            <p><b>Objective:</b> {summary["objective"]}</p>
            <span class="tag">enterprise workflow</span>
            <span class="tag">incident response</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown("### Workflow replay")
    components.html(
        build_workflow_replay_html(
            df=df,
            scenario=scenario,
            animate=st.session_state.workflow_animate_now,
        ),
        height=430,
        scrolling=False,
    )

    st.markdown("### Scenario diagnosis")
    st.markdown(
        f"""
        <div class="module-card">
            <h3>{scenario}</h3>
            <p>{summary["summary"]}</p>
            <p><b>Root cause:</b> {summary["root_cause"]}</p>
            <p><b>Containment:</b> {summary["containment"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.workflow_animate_now:
    st.session_state.workflow_animate_now = False

st.success(f"Active workflow: {scenario}. Containment: {summary['containment']}.")

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Root cause", summary["root_cause"], "First abnormal source")

with m2:
    metric_card("Containment", summary["containment"], "Where the control acts")

with m3:
    metric_card("Max risk", str(max_risk), "Highest risk score")

with m4:
    metric_card("High-risk steps", str(high_risk_steps), "Risk score ≥ 0.70")

st.divider()

section(
    "Risk over workflow",
    "The chart shows how risk changes across the enterprise incident workflow.",
)

st.plotly_chart(
    build_risk_chart(df),
    use_container_width=True,
    config={"displayModeBar": False},
)

st.divider()

section(
    "Execution trace",
    "Each row records the event, status, and risk score for one workflow step.",
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=320,
)

st.divider()

section(
    "Experiment comparison",
    "This table compares the available workflow scenarios.",
)

st.dataframe(
    build_comparison_table(),
    use_container_width=True,
    hide_index=True,
    height=220,
)

st.divider()

section(
    "Engineering interpretation",
    "This page gives the project a realistic enterprise baseline. It shows how an incident moves through specialised agents, where evidence is checked, where risk appears, and where controls block, contain, or escalate unsafe behaviour.",
)