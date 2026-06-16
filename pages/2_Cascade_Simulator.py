import html

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

from src.ui import apply_global_style, page_header, metric_card, section

st.set_page_config(
    page_title="Cascade Simulator",
    page_icon="🧩",
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

SCENARIOS = {
    "Hallucinated root cause": {
        "seed_agent": "Knowledge Agent",
        "fault": "Knowledge Agent invents database saturation without log evidence.",
        "risk": [0.10, 0.16, 0.24, 0.82, 0.92, 0.88, 0.35, 0.20],
    },
    "Missing evidence": {
        "seed_agent": "Log Analysis Agent",
        "fault": "Log Analysis Agent fails to retrieve logs, but the workflow continues.",
        "risk": [0.10, 0.18, 0.74, 0.68, 0.76, 0.70, 0.58, 0.42],
    },
    "Prompt injection attempt": {
        "seed_agent": "Action Agent",
        "fault": "Action Agent receives an unsafe instruction to ignore verification.",
        "risk": [0.10, 0.14, 0.18, 0.22, 0.98, 0.96, 0.30, 0.16],
    },
    "False success declaration": {
        "seed_agent": "Verification Agent",
        "fault": "Verification Agent declares success without hard evidence.",
        "risk": [0.10, 0.15, 0.22, 0.28, 0.40, 0.91, 0.74, 0.68],
    },
}


STATUS_COLORS = {
    "pending": "#475569",
    "clean": "#38bdf8",
    "fault seed": "#ef4444",
    "contaminated": "#f97316",
    "blocked": "#facc15",
    "protected": "#22c55e",
}


def simulate_cascade(scenario_name: str, control_mode: str):
    scenario = SCENARIOS[scenario_name]
    seed_agent = scenario["seed_agent"]
    seed_index = AGENTS.index(seed_agent)

    if control_mode == "No control layer":
        containment_index = None
        control_summary = "No control layer is active, so risky context can propagate downstream."
        final_decision = "Cascaded"

    elif control_mode == "EvidenceGate verification":
        containment_index = AGENTS.index("Verification Agent")
        control_summary = "EvidenceGate blocks unsupported or unverifiable action at the verification step."
        final_decision = "Blocked"

    else:
        containment_index = min(seed_index + 1, AGENTS.index("Safety Agent"))
        control_summary = "CASCADE isolation quarantines risky context close to the fault seed."
        final_decision = "Contained"

    rows = []

    for idx, agent in enumerate(AGENTS):
        base_risk = scenario["risk"][idx]

        if idx < seed_index:
            status = "clean"
            trace_label = "normal"
            event = "Normal workflow step before the fault seed."
            risk_score = min(base_risk, 0.25)

        elif idx == seed_index:
            status = "fault seed"
            trace_label = "fault_seed"
            event = scenario["fault"]
            risk_score = base_risk

        else:
            if control_mode == "No control layer":
                status = "contaminated"
                trace_label = "propagated"
                event = "Risky context was reused by this downstream agent."
                risk_score = max(base_risk, 0.72)

            elif containment_index is not None and idx < containment_index:
                status = "contaminated"
                trace_label = "propagated"
                event = "Risky context reached this agent before containment."
                risk_score = base_risk

            elif containment_index is not None and idx == containment_index:
                status = "blocked"
                trace_label = "contained"
                event = "Control layer stopped the propagation path."
                risk_score = base_risk

            else:
                status = "protected"
                trace_label = "protected"
                event = "Downstream agent protected after containment."
                risk_score = min(base_risk, 0.30)

        rows.append(
            {
                "step": idx + 1,
                "agent": agent,
                "scenario": scenario_name,
                "control_mode": control_mode,
                "event": event,
                "trace_label": trace_label,
                "risk_score": round(risk_score, 2),
                "status": status,
            }
        )

    df = pd.DataFrame(rows)

    contaminated_count = int((df["status"] == "contaminated").sum())
    affected_count = int(df["status"].isin(["fault seed", "contaminated", "blocked"]).sum())

    metrics = {
        "fault_seed": seed_agent,
        "fault": scenario["fault"],
        "max_risk": round(df["risk_score"].max(), 2),
        "blast_radius": contaminated_count,
        "propagation_depth": max(0, affected_count - 1),
        "containment_point": "None" if containment_index is None else AGENTS[containment_index],
        "containment_step": None if containment_index is None else containment_index + 1,
        "final_decision": final_decision,
        "control_summary": control_summary,
    }

    return df, metrics


def build_svg_path(stop_step: int):
    selected_agents = AGENTS[:stop_step]
    commands = []

    for idx, agent in enumerate(selected_agents):
        x, y = SVG_POSITIONS[agent]

        if idx == 0:
            commands.append(f"M {x} {y}")
        else:
            commands.append(f"L {x} {y}")

    return " ".join(commands)


def build_animated_cascade_html(df: pd.DataFrame, metrics: dict):
    stop_step = metrics["containment_step"] or len(AGENTS)
    motion_path = build_svg_path(stop_step)
    duration = max(3.0, stop_step * 0.55)

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
        status = df.loc[df["agent"] == agent, "status"].iloc[0]
        final_color = STATUS_COLORS[status]

        if idx + 1 <= stop_step:
            begin_time = idx * 0.55
        else:
            begin_time = duration + 0.25

        safe_agent = html.escape(agent)
        safe_status = html.escape(status)

        node_items.append(
            f"""
            <g>
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
                <div class="title">Live cascade replay</div>
                <div class="status">Stops at: {html.escape(metrics["containment_point"])}</div>
            </div>

            <svg viewBox="0 0 900 330" width="100%" height="390">
                {"".join(edge_lines)}

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

                {"".join(node_items)}

                <circle r="10" fill="#ffffff" stroke="#38bdf8" stroke-width="5" class="runner">
                    <animateMotion dur="{duration}s"
                                   path="{motion_path}"
                                   fill="freeze"
                                   calcMode="linear" />
                </circle>
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
            mode="lines+markers",
            text=df["agent"],
            hovertemplate="Step %{x}<br>%{text}<br>Risk: %{y}<extra></extra>",
            line=dict(width=3),
            marker=dict(size=8),
        )
    )

    fig.update_layout(
        height=340,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Workflow step", gridcolor="rgba(148,163,184,0.15)"),
        yaxis=dict(title="Risk score", range=[0, 1], gridcolor="rgba(148,163,184,0.15)"),
    )

    return fig


def compare_controls(scenario_name: str):
    rows = []

    for control in [
        "No control layer",
        "EvidenceGate verification",
        "CASCADE isolation",
    ]:
        df, metrics = simulate_cascade(scenario_name, control)

        rows.append(
            {
                "scenario": scenario_name,
                "control_mode": control,
                "max_risk": metrics["max_risk"],
                "blast_radius": metrics["blast_radius"],
                "propagation_depth": metrics["propagation_depth"],
                "containment_point": metrics["containment_point"],
                "final_decision": metrics["final_decision"],
            }
        )

    return pd.DataFrame(rows)


page_header(
    "Cascade Simulator",
    "A controlled experiment showing how one faulty agent output can spread across a multi-agent workflow, and how verification or isolation controls reduce the blast radius.",
)

scenario_options = list(SCENARIOS.keys())

control_options = [
    "No control layer",
    "EvidenceGate verification",
    "CASCADE isolation",
]

if "cascade_scenario" not in st.session_state:
    st.session_state.cascade_scenario = "Hallucinated root cause"

if "cascade_control" not in st.session_state:
    st.session_state.cascade_control = "No control layer"

left, right = st.columns([1, 1.7])

with left:
    st.markdown("### Simulation control")

    selected_scenario = st.selectbox(
        "Failure seed",
        scenario_options,
        index=scenario_options.index(st.session_state.cascade_scenario),
    )

    selected_control = st.selectbox(
        "Control strategy",
        control_options,
        index=control_options.index(st.session_state.cascade_control),
    )

    if st.button("Run cascade simulation", use_container_width=True):
        st.session_state.cascade_scenario = selected_scenario
        st.session_state.cascade_control = selected_control
        st.rerun()

scenario = st.session_state.cascade_scenario
control = st.session_state.cascade_control

df, metrics = simulate_cascade(scenario, control)

with left:
    st.markdown(
        f"""
        <div class="module-card">
            <h3>Active experiment</h3>
            <p><b>Scenario:</b> {scenario}</p>
            <p><b>Fault seed:</b> {metrics["fault_seed"]}</p>
            <p><b>Injected fault:</b> {metrics["fault"]}</p>
            <span class="tag">cascade test</span>
            <span class="tag">blast radius</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown("### Animated cascade graph")
    components.html(
        build_animated_cascade_html(df, metrics),
        height=430,
        scrolling=False,
    )

st.success(f"Active run: {scenario} with {control}. {metrics['control_summary']}")

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Fault seed", metrics["fault_seed"], "Initial source of risky context")

with m2:
    metric_card("Blast radius", str(metrics["blast_radius"]), "Contaminated downstream agents")

with m3:
    metric_card("Containment point", metrics["containment_point"], "Where propagation stopped")

with m4:
    metric_card("Final decision", metrics["final_decision"], "Cascaded, blocked, or contained")

st.divider()

section(
    "Risk trend",
    "The graph shows whether risk spreads downstream or drops after containment.",
)

st.plotly_chart(
    build_risk_chart(df),
    use_container_width=True,
    config={"displayModeBar": False},
)

st.divider()

section(
    "Cascade trace",
    "This table records the state of each agent during the cascade simulation.",
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=330,
)

st.divider()

section(
    "Control comparison",
    "This table compares the effect of no control, verification, and isolation for the selected failure seed.",
)

st.dataframe(
    compare_controls(scenario),
    use_container_width=True,
    hide_index=True,
    height=180,
)

st.divider()

section("Legend")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown('<span class="tag">Clean</span>', unsafe_allow_html=True)
    st.caption("No risky context received")

with c2:
    st.markdown('<span class="danger-tag">Fault seed</span>', unsafe_allow_html=True)
    st.caption("Initial source of failure")

with c3:
    st.markdown('<span class="warning-tag">Contaminated</span>', unsafe_allow_html=True)
    st.caption("Risky context reused")

with c4:
    st.markdown('<span class="warning-tag">Blocked</span>', unsafe_allow_html=True)
    st.caption("Control stopped propagation")

with c5:
    st.markdown('<span class="success-tag">Protected</span>', unsafe_allow_html=True)
    st.caption("Downstream protected")

st.divider()

section(
    "Engineering interpretation",
    "This module shows why multi-agent AI systems need explicit control layers. Without containment, one unsupported claim or unsafe instruction can move downstream and influence later agents. EvidenceGate blocks unsupported actions at verification time. CASCADE isolation reduces the blast radius by quarantining risky context closer to the source.",
)