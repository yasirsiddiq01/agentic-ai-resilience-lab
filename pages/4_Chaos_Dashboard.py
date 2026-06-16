import html

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

from src.ui import apply_global_style, page_header, metric_card, section

st.set_page_config(
    page_title="Chaos Dashboard",
    page_icon="📊",
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
    "clean": "#38bdf8",
    "fault injected": "#ef4444",
    "propagated": "#f97316",
    "contained": "#facc15",
    "recovered": "#22c55e",
}


FAULTS = {
    "No fault": {
        "seed_agent": "None",
        "description": "Baseline workflow with no injected fault.",
        "failure_mode": "None",
        "base_risk": [0.08, 0.12, 0.16, 0.18, 0.22, 0.10, 0.07, 0.05],
    },
    "Stale retrieval": {
        "seed_agent": "Knowledge Agent",
        "description": "Knowledge Agent retrieves an outdated runbook and passes it to the Action Agent.",
        "failure_mode": "Outdated context reuse",
        "base_risk": [0.10, 0.14, 0.22, 0.68, 0.82, 0.76, 0.42, 0.28],
    },
    "Missing logs": {
        "seed_agent": "Log Analysis Agent",
        "description": "Log Analysis Agent cannot retrieve logs, but the workflow continues with weak evidence.",
        "failure_mode": "Missing evidence",
        "base_risk": [0.10, 0.18, 0.74, 0.66, 0.78, 0.70, 0.50, 0.36],
    },
    "Prompt injection": {
        "seed_agent": "Action Agent",
        "description": "Action Agent receives an unsafe instruction to ignore verification and close the incident.",
        "failure_mode": "Instruction contamination",
        "base_risk": [0.10, 0.14, 0.18, 0.22, 0.96, 0.94, 0.38, 0.22],
    },
    "False verification": {
        "seed_agent": "Verification Agent",
        "description": "Verification Agent declares success without hard tool evidence.",
        "failure_mode": "Incorrect verification",
        "base_risk": [0.10, 0.15, 0.20, 0.28, 0.44, 0.90, 0.78, 0.64],
    },
    "Over-permissioned action": {
        "seed_agent": "Action Agent",
        "description": "Action Agent attempts a remediation action outside its allowed permission scope.",
        "failure_mode": "Unsafe delegation / permission breach",
        "base_risk": [0.10, 0.16, 0.22, 0.30, 0.88, 0.84, 0.72, 0.46],
    },
}

RECOVERY_MODES = {
    "No recovery control": {
        "type": "none",
        "description": "The workflow has no explicit containment or recovery control.",
    },
    "EvidenceGate": {
        "type": "verification",
        "description": "The workflow blocks unsupported recommendations at the Verification Agent.",
    },
    "Safety Guard": {
        "type": "safety",
        "description": "The workflow blocks unsafe or over-permissioned actions at the Safety Agent.",
    },
    "CASCADE Isolation": {
        "type": "isolation",
        "description": "The workflow quarantines risky context close to the source and protects downstream agents.",
    },
}


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def intensity_factor(level: str) -> float:
    if level == "Low":
        return 0.85
    if level == "High":
        return 1.15
    return 1.0


def determine_containment(seed_agent: str, recovery_mode: str):
    if seed_agent == "None":
        return None

    seed_index = AGENTS.index(seed_agent)
    mode = RECOVERY_MODES[recovery_mode]["type"]

    if mode == "none":
        return None

    if mode == "verification":
        return AGENTS.index("Verification Agent")

    if mode == "safety":
        return AGENTS.index("Safety Agent")

    if mode == "isolation":
        return min(seed_index + 1, AGENTS.index("Safety Agent"))

    return None


def run_chaos_experiment(fault_name: str, recovery_mode: str, intensity: str):
    fault = FAULTS[fault_name]
    seed_agent = fault["seed_agent"]
    factor = intensity_factor(intensity)
    containment_index = determine_containment(seed_agent, recovery_mode)

    seed_index = None if seed_agent == "None" else AGENTS.index(seed_agent)
    rows = []

    for idx, agent in enumerate(AGENTS):
        risk = clamp(fault["base_risk"][idx] * factor)

        if seed_index is None:
            status = "clean"
            event = "Baseline step completed normally."
            action = "continue"

        elif idx < seed_index:
            status = "clean"
            event = "Normal step before injected fault."
            action = "continue"

        elif idx == seed_index:
            status = "fault injected"
            event = fault["description"]
            action = "detect"

        else:
            if containment_index is None:
                status = "propagated"
                event = "Risky context continued downstream without containment."
                action = "continue"

            elif idx < containment_index:
                status = "propagated"
                event = "Risky context reached this step before containment."
                action = "monitor"

            elif idx == containment_index:
                status = "contained"
                event = "Recovery control stopped the propagation path."
                action = "block"

            else:
                status = "recovered"
                event = "Downstream step protected after containment."
                action = "recover"
                risk = min(risk, 0.30)

        rows.append(
            {
                "step": idx + 1,
                "agent": agent,
                "fault": fault_name,
                "recovery_mode": recovery_mode,
                "event": event,
                "failure_mode": fault["failure_mode"],
                "risk_score": round(risk, 2),
                "status": status,
                "action": action,
            }
        )

    df = pd.DataFrame(rows)

    if seed_index is None:
        metrics = {
            "fault_seed": "None",
            "detection_step": "None",
            "containment_step": "Not required",
            "containment_index": len(AGENTS) - 1,
            "recovery_result": "Clean baseline",
            "recovery_rate": 100,
            "containment_quality": "Healthy",
            "blast_radius": 0,
            "affected_steps": 0,
            "steps_to_containment": 0,
            "max_risk": round(df["risk_score"].max(), 2),
            "recovery_description": RECOVERY_MODES[recovery_mode]["description"],
        }
        return df, metrics

    if containment_index is None:
        containment_step = "None"
        containment_for_animation = len(AGENTS) - 1
        recovery_result = "Failed"
        containment_quality = "Uncontrolled"
        recovery_rate = 0
        steps_to_containment = len(AGENTS) - seed_index
    else:
        containment_step = AGENTS[containment_index]
        containment_for_animation = containment_index
        recovery_result = "Recovered"
        containment_quality = "Controlled"
        recovery_rate = 100
        steps_to_containment = containment_index - seed_index

    metrics = {
        "fault_seed": seed_agent,
        "detection_step": AGENTS[seed_index],
        "containment_step": containment_step,
        "containment_index": containment_for_animation,
        "recovery_result": recovery_result,
        "recovery_rate": recovery_rate,
        "containment_quality": containment_quality,
        "blast_radius": int((df["status"] == "propagated").sum()),
        "affected_steps": int(df["status"].isin(["fault injected", "propagated", "contained"]).sum()),
        "steps_to_containment": steps_to_containment,
        "max_risk": round(df["risk_score"].max(), 2),
        "recovery_description": RECOVERY_MODES[recovery_mode]["description"],
    }

    return df, metrics


def build_svg_path(stop_index: int):
    selected_agents = AGENTS[: stop_index + 1]
    commands = []

    for idx, agent in enumerate(selected_agents):
        x, y = SVG_POSITIONS[agent]
        if idx == 0:
            commands.append(f"M {x} {y}")
        else:
            commands.append(f"L {x} {y}")

    return " ".join(commands)


def build_chaos_replay_html(df: pd.DataFrame, metrics: dict, fault: str, recovery: str, animate: bool):
    stop_index = metrics["containment_index"]
    motion_path = build_svg_path(stop_index)
    duration = max(3.0, (stop_index + 1) * 0.55)

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

        if idx <= stop_index:
            begin_time = idx * 0.55
        else:
            begin_time = duration + 0.5

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
        stop_agent = AGENTS[stop_index]
        stop_x, stop_y = SVG_POSITIONS[stop_agent]
        runner_path = f"""
            <path d="{motion_path}"
                  fill="none"
                  stroke="rgba(56,189,248,0.95)"
                  stroke-width="5"
                  stroke-linecap="round" />
            <circle cx="{stop_x}" cy="{stop_y}" r="10"
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
                <div class="title">Chaos experiment replay</div>
                <div class="status">Fault: {html.escape(fault)} | Recovery: {html.escape(recovery)}</div>
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
            marker=dict(size=9),
            hovertemplate="<b>%{text}</b><br>Step %{x}<br>Risk: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Workflow step", gridcolor="rgba(148,163,184,0.15)", dtick=1),
        yaxis=dict(title="Risk score", range=[0, 1], gridcolor="rgba(148,163,184,0.15)"),
    )

    return fig


def build_status_bar(df: pd.DataFrame):
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=status_counts["status"],
            y=status_counts["count"],
            text=status_counts["count"],
            textposition="outside",
            hovertemplate="Status: %{x}<br>Count: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Agent status", gridcolor="rgba(148,163,184,0.15)"),
        yaxis=dict(title="Count", gridcolor="rgba(148,163,184,0.15)", dtick=1),
    )

    return fig


def build_experiment_matrix(fault_name: str, intensity: str):
    rows = []

    for recovery_mode in RECOVERY_MODES.keys():
        df, metrics = run_chaos_experiment(fault_name, recovery_mode, intensity)
        rows.append(
            {
                "fault": fault_name,
                "recovery_mode": recovery_mode,
                "max_risk": metrics["max_risk"],
                "blast_radius": metrics["blast_radius"],
                "containment_step": metrics["containment_step"],
                "recovery_result": metrics["recovery_result"],
                "steps_to_containment": metrics["steps_to_containment"],
            }
        )

    return pd.DataFrame(rows)


page_header(
    "Chaos Dashboard",
    "Controlled fault injection for multi-agent workflows. This module tests whether the system detects, contains, and recovers from injected failures.",
)

fault_options = list(FAULTS.keys())
recovery_options = list(RECOVERY_MODES.keys())
intensity_options = ["Low", "Medium", "High"]

if "chaos_fault" not in st.session_state:
    st.session_state.chaos_fault = "Prompt injection"

if "chaos_recovery" not in st.session_state:
    st.session_state.chaos_recovery = "EvidenceGate"

if "chaos_intensity" not in st.session_state:
    st.session_state.chaos_intensity = "Medium"

if "chaos_animate_now" not in st.session_state:
    st.session_state.chaos_animate_now = False

left, right = st.columns([1, 1.7])

with left:
    st.markdown("### Chaos controls")

    selected_fault = st.selectbox(
        "Injected fault",
        fault_options,
        index=fault_options.index(st.session_state.chaos_fault),
    )

    selected_recovery = st.selectbox(
        "Recovery strategy",
        recovery_options,
        index=recovery_options.index(st.session_state.chaos_recovery),
    )

    selected_intensity = st.selectbox(
        "Fault intensity",
        intensity_options,
        index=intensity_options.index(st.session_state.chaos_intensity),
    )

    if st.button("Run chaos experiment", use_container_width=True):
        st.session_state.chaos_fault = selected_fault
        st.session_state.chaos_recovery = selected_recovery
        st.session_state.chaos_intensity = selected_intensity
        st.session_state.chaos_animate_now = True
        st.rerun()

fault = st.session_state.chaos_fault
recovery = st.session_state.chaos_recovery
intensity = st.session_state.chaos_intensity

df, metrics = run_chaos_experiment(fault, recovery, intensity)

with left:
    st.markdown(
        f"""
        <div class="module-card">
            <h3>Active chaos run</h3>
            <p><b>Fault:</b> {fault}</p>
            <p><b>Failure mode:</b> {FAULTS[fault]["failure_mode"]}</p>
            <p><b>Intensity:</b> {intensity}</p>
            <span class="tag">fault injection</span>
            <span class="tag">recovery test</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown("### Chaos replay")
    components.html(
        build_chaos_replay_html(
            df=df,
            metrics=metrics,
            fault=fault,
            recovery=recovery,
            animate=st.session_state.chaos_animate_now,
        ),
        height=430,
        scrolling=False,
    )

    st.markdown("### Experiment objective")
    st.markdown(
        f"""
        <div class="module-card">
            <h3>{fault}</h3>
            <p>{FAULTS[fault]["description"]}</p>
            <p><b>Recovery control:</b> {metrics["recovery_description"]}</p>
            <span class="tag">detection</span>
            <span class="tag">containment</span>
            <span class="tag">observability</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.chaos_animate_now:
    st.session_state.chaos_animate_now = False

st.success(f"Active run: {fault} with {recovery}. Result: {metrics['recovery_result']}.")

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Detection point", metrics["detection_step"], "Where the injected fault appears")

with m2:
    metric_card("Containment point", metrics["containment_step"], "Where recovery control acts")

with m3:
    metric_card("Blast radius", str(metrics["blast_radius"]), "Steps affected before containment")

with m4:
    metric_card("Recovery result", metrics["recovery_result"], metrics["containment_quality"])

m5, m6, m7, m8 = st.columns(4)

with m5:
    metric_card("Max risk", str(metrics["max_risk"]), "Highest risk reached")

with m6:
    metric_card("Affected steps", str(metrics["affected_steps"]), "Fault, propagation, and containment steps")

with m7:
    metric_card("Steps to containment", str(metrics["steps_to_containment"]), "Lower is better")

with m8:
    metric_card("Recovery rate", f"{metrics['recovery_rate']}%", "Recovered or uncontrolled")

st.divider()

chart_col, bar_col = st.columns([1.3, 1])

with chart_col:
    section(
        "Risk over workflow",
        "This chart shows how risk rises after fault injection and whether it drops after recovery.",
    )
    st.plotly_chart(
        build_risk_chart(df),
        use_container_width=True,
        config={"displayModeBar": False},
    )

with bar_col:
    section(
        "Agent status distribution",
        "This chart shows how many agents are clean, affected, contained, or recovered.",
    )
    st.plotly_chart(
        build_status_bar(df),
        use_container_width=True,
        config={"displayModeBar": False},
    )

st.divider()

section(
    "Chaos execution trace",
    "Each row shows how the injected fault affected an agent step and what action the control layer took.",
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=330,
)

st.divider()

section(
    "Recovery strategy comparison",
    "This table compares recovery controls for the selected fault and intensity.",
)

st.dataframe(
    build_experiment_matrix(fault, intensity),
    use_container_width=True,
    hide_index=True,
    height=220,
)

st.divider()

section(
    "Engineering interpretation",
    "The Chaos Dashboard tests whether the agent workflow behaves safely under controlled failure. A serious agentic AI system should expose failure signals, reduce blast radius, block unsupported actions, and recover or escalate when confidence and evidence are insufficient.",
)
