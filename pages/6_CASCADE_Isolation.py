import html

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go

from src.ui import apply_global_style, page_header, metric_card, section

st.set_page_config(
    page_title="CASCADE Isolation",
    page_icon="🛡️",
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
    "trusted": "#38bdf8",
    "fault seed": "#ef4444",
    "contaminated": "#f97316",
    "exposed": "#f97316",
    "isolated": "#facc15",
    "protected": "#22c55e",
    "recovered": "#22c55e",
}


SCENARIOS = {
    "Hallucinated root cause": {
        "seed_agent": "Knowledge Agent",
        "fault": "Unsupported database-saturation claim introduced by Knowledge Agent.",
        "contaminated_claim": "database_saturation=true",
        "required_evidence": "database logs, CPU saturation metrics, connection pool evidence",
        "risk": [0.10, 0.16, 0.24, 0.82, 0.92, 0.88, 0.35, 0.20],
    },
    "Missing evidence": {
        "seed_agent": "Log Analysis Agent",
        "fault": "Log retrieval fails but downstream reasoning continues with weak support.",
        "contaminated_claim": "logs_confirm_gateway_timeout=unknown",
        "required_evidence": "payment-api logs, gateway logs, request failure samples",
        "risk": [0.10, 0.18, 0.74, 0.68, 0.76, 0.70, 0.58, 0.42],
    },
    "Prompt injection attempt": {
        "seed_agent": "Action Agent",
        "fault": "Unsafe instruction attempts to bypass verification and close the incident.",
        "contaminated_claim": "ignore_verification=true",
        "required_evidence": "policy check, instruction provenance, allowed action list",
        "risk": [0.10, 0.14, 0.18, 0.22, 0.98, 0.96, 0.30, 0.16],
    },
    "False success declaration": {
        "seed_agent": "Verification Agent",
        "fault": "Verification Agent declares success without hard health-check evidence.",
        "contaminated_claim": "incident_resolved=true",
        "required_evidence": "health endpoint, error-rate drop, alert recovery status",
        "risk": [0.10, 0.15, 0.22, 0.28, 0.40, 0.91, 0.74, 0.68],
    },
    "Over-permissioned action": {
        "seed_agent": "Action Agent",
        "fault": "Action Agent attempts a production remediation outside its permission scope.",
        "contaminated_claim": "execute_production_restart=true",
        "required_evidence": "role permission, approval status, change window policy",
        "risk": [0.10, 0.16, 0.22, 0.30, 0.88, 0.84, 0.72, 0.46],
    },
}

ISOLATION_MODES = {
    "No isolation": {
        "description": "The workflow does not quarantine risky context. Downstream agents may reuse the contaminated claim.",
        "strategy": "none",
    },
    "EvidenceGate only": {
        "description": "Unsupported action is blocked at the Verification Agent, but earlier contaminated context may still reach intermediate agents.",
        "strategy": "verification",
    },
    "CASCADE isolation": {
        "description": "Risky context is quarantined close to the source and downstream agents receive sanitized context.",
        "strategy": "isolation",
    },
    "CASCADE isolation + rollback": {
        "description": "Risky context is quarantined and the workflow rolls back to the last trusted step before continuing.",
        "strategy": "rollback",
    },
}


def determine_isolation_point(seed_index: int, mode: str):
    strategy = ISOLATION_MODES[mode]["strategy"]

    if strategy == "none":
        return None

    if strategy == "verification":
        return AGENTS.index("Verification Agent")

    if strategy == "isolation":
        return min(seed_index + 1, AGENTS.index("Safety Agent"))

    if strategy == "rollback":
        return min(seed_index + 1, AGENTS.index("Safety Agent"))

    return None


def simulate_isolation(scenario_name: str, isolation_mode: str):
    scenario = SCENARIOS[scenario_name]
    seed_agent = scenario["seed_agent"]
    seed_index = AGENTS.index(seed_agent)
    isolation_index = determine_isolation_point(seed_index, isolation_mode)
    strategy = ISOLATION_MODES[isolation_mode]["strategy"]

    rows = []

    for idx, agent in enumerate(AGENTS):
        base_risk = scenario["risk"][idx]

        if idx < seed_index:
            status = "trusted"
            context_state = "clean"
            action = "continue"
            event = "Trusted workflow step before fault seed."
            risk = min(base_risk, 0.25)

        elif idx == seed_index:
            status = "fault seed"
            context_state = "contaminated"
            action = "mark risky"
            event = scenario["fault"]
            risk = base_risk

        else:
            if strategy == "none":
                status = "contaminated"
                context_state = "contaminated"
                action = "continue"
                event = "Contaminated context reused without isolation."
                risk = max(base_risk, 0.72)

            elif isolation_index is not None and idx < isolation_index:
                status = "exposed"
                context_state = "contaminated"
                action = "monitor"
                event = "Risky context reached this agent before isolation."
                risk = base_risk

            elif isolation_index is not None and idx == isolation_index:
                status = "isolated"
                context_state = "quarantined"
                action = "quarantine"
                event = "CASCADE control quarantined the contaminated context."
                risk = base_risk

            else:
                if strategy == "rollback":
                    status = "recovered"
                    context_state = "rolled back"
                    action = "resume from trusted state"
                    event = "Workflow resumed from last trusted context after rollback."
                    risk = min(base_risk, 0.22)
                else:
                    status = "protected"
                    context_state = "sanitized"
                    action = "continue with safe context"
                    event = "Downstream agent received sanitized context."
                    risk = min(base_risk, 0.30)

        rows.append(
            {
                "step": idx + 1,
                "agent": agent,
                "scenario": scenario_name,
                "isolation_mode": isolation_mode,
                "event": event,
                "context_state": context_state,
                "risk_score": round(risk, 2),
                "status": status,
                "action": action,
            }
        )

    df = pd.DataFrame(rows)

    contaminated_agents = int((df["context_state"] == "contaminated").sum())
    protected_agents = int(df["status"].isin(["protected", "recovered"]).sum())
    quarantined = int((df["context_state"] == "quarantined").sum())

    if strategy == "none":
        final_decision = "Unsafe propagation"
        isolation_point = "None"
        rollback_point = "None"
        containment_quality = "Uncontrolled"
        isolation_index_for_animation = len(AGENTS) - 1

    elif strategy == "verification":
        final_decision = "Blocked late"
        isolation_point = AGENTS[isolation_index]
        rollback_point = "None"
        containment_quality = "Partial"
        isolation_index_for_animation = isolation_index

    elif strategy == "isolation":
        final_decision = "Contained"
        isolation_point = AGENTS[isolation_index]
        rollback_point = "None"
        containment_quality = "Controlled"
        isolation_index_for_animation = isolation_index

    else:
        final_decision = "Recovered"
        isolation_point = AGENTS[isolation_index]
        rollback_index = max(0, seed_index - 1)
        rollback_point = AGENTS[rollback_index]
        containment_quality = "Controlled + rollback"
        isolation_index_for_animation = isolation_index

    metrics = {
        "fault_seed": seed_agent,
        "contaminated_claim": scenario["contaminated_claim"],
        "required_evidence": scenario["required_evidence"],
        "isolation_point": isolation_point,
        "rollback_point": rollback_point,
        "isolation_index": isolation_index_for_animation,
        "contaminated_agents": contaminated_agents,
        "protected_agents": protected_agents,
        "quarantined_steps": quarantined,
        "max_risk": round(df["risk_score"].max(), 2),
        "final_decision": final_decision,
        "containment_quality": containment_quality,
        "mode_description": ISOLATION_MODES[isolation_mode]["description"],
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


def build_isolation_replay_html(df: pd.DataFrame, metrics: dict, scenario: str, mode: str, animate: bool):
    stop_index = metrics["isolation_index"]
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
                <div class="title">CASCADE isolation replay</div>
                <div class="status">Scenario: {html.escape(scenario)} | Mode: {html.escape(mode)}</div>
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
        height=340,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Workflow step", gridcolor="rgba(148,163,184,0.15)", dtick=1),
        yaxis=dict(title="Risk score", range=[0, 1], gridcolor="rgba(148,163,184,0.15)"),
    )

    return fig


def build_context_state_chart(df: pd.DataFrame):
    counts = df["context_state"].value_counts().reset_index()
    counts.columns = ["context_state", "count"]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=counts["context_state"],
            y=counts["count"],
            text=counts["count"],
            textposition="outside",
            hovertemplate="Context state: %{x}<br>Count: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=30, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#e5e7eb"),
        xaxis=dict(title="Context state", gridcolor="rgba(148,163,184,0.15)"),
        yaxis=dict(title="Count", gridcolor="rgba(148,163,184,0.15)", dtick=1),
    )

    return fig


def build_strategy_comparison(scenario_name: str):
    rows = []

    for mode in ISOLATION_MODES.keys():
        df, metrics = simulate_isolation(scenario_name, mode)
        rows.append(
            {
                "scenario": scenario_name,
                "isolation_mode": mode,
                "contaminated_agents": metrics["contaminated_agents"],
                "protected_agents": metrics["protected_agents"],
                "isolation_point": metrics["isolation_point"],
                "rollback_point": metrics["rollback_point"],
                "final_decision": metrics["final_decision"],
                "containment_quality": metrics["containment_quality"],
            }
        )

    return pd.DataFrame(rows)


page_header(
    "CASCADE Isolation",
    "Semantic fault isolation for multi-agent workflows. This module quarantines contaminated context, protects downstream agents, and optionally rolls back to the last trusted step.",
)

scenario_options = list(SCENARIOS.keys())
mode_options = list(ISOLATION_MODES.keys())

if "isolation_scenario" not in st.session_state:
    st.session_state.isolation_scenario = "Prompt injection attempt"

if "isolation_mode" not in st.session_state:
    st.session_state.isolation_mode = "CASCADE isolation"

if "isolation_animate_now" not in st.session_state:
    st.session_state.isolation_animate_now = False

left, right = st.columns([1, 1.7])

with left:
    st.markdown("### Isolation controls")

    selected_scenario = st.selectbox(
        "Failure scenario",
        scenario_options,
        index=scenario_options.index(st.session_state.isolation_scenario),
    )

    selected_mode = st.selectbox(
        "Isolation strategy",
        mode_options,
        index=mode_options.index(st.session_state.isolation_mode),
    )

    if st.button("Run isolation test", use_container_width=True):
        st.session_state.isolation_scenario = selected_scenario
        st.session_state.isolation_mode = selected_mode
        st.session_state.isolation_animate_now = True
        st.rerun()

scenario = st.session_state.isolation_scenario
mode = st.session_state.isolation_mode

df, metrics = simulate_isolation(scenario, mode)

with left:
    st.markdown(
        f"""
        <div class="module-card">
            <h3>Active isolation test</h3>
            <p><b>Scenario:</b> {scenario}</p>
            <p><b>Fault seed:</b> {metrics["fault_seed"]}</p>
            <p><b>Contaminated claim:</b> {metrics["contaminated_claim"]}</p>
            <span class="tag">semantic isolation</span>
            <span class="tag">quarantine</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown("### Isolation replay")
    components.html(
        build_isolation_replay_html(
            df=df,
            metrics=metrics,
            scenario=scenario,
            mode=mode,
            animate=st.session_state.isolation_animate_now,
        ),
        height=430,
        scrolling=False,
    )

    st.markdown("### Isolation objective")
    st.markdown(
        f"""
        <div class="module-card">
            <h3>{mode}</h3>
            <p>{metrics["mode_description"]}</p>
            <p><b>Required evidence:</b> {metrics["required_evidence"]}</p>
            <span class="tag">context control</span>
            <span class="tag">rollback</span>
            <span class="tag">blast-radius reduction</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.isolation_animate_now:
    st.session_state.isolation_animate_now = False

st.success(f"Active run: {scenario} with {mode}. Final decision: {metrics['final_decision']}.")

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Isolation point", metrics["isolation_point"], "Where contaminated context is stopped")

with m2:
    metric_card("Rollback point", metrics["rollback_point"], "Last trusted step used for recovery")

with m3:
    metric_card("Contaminated agents", str(metrics["contaminated_agents"]), "Lower is better")

with m4:
    metric_card("Protected agents", str(metrics["protected_agents"]), "Downstream agents shielded")

m5, m6, m7, m8 = st.columns(4)

with m5:
    metric_card("Quarantine steps", str(metrics["quarantined_steps"]), "Explicit quarantine actions")

with m6:
    metric_card("Max risk", str(metrics["max_risk"]), "Highest risk reached")

with m7:
    metric_card("Final decision", metrics["final_decision"], "Unsafe, blocked, contained, or recovered")

with m8:
    metric_card("Containment quality", metrics["containment_quality"], "Control quality assessment")

st.divider()

chart_col, state_col = st.columns([1.3, 1])

with chart_col:
    section(
        "Risk before and after isolation",
        "This chart shows whether risk remains high or drops after quarantine, sanitization, or rollback.",
    )
    st.plotly_chart(
        build_risk_chart(df),
        use_container_width=True,
        config={"displayModeBar": False},
    )

with state_col:
    section(
        "Context state distribution",
        "This chart counts clean, contaminated, quarantined, sanitized, and rolled-back context states.",
    )
    st.plotly_chart(
        build_context_state_chart(df),
        use_container_width=True,
        config={"displayModeBar": False},
    )

st.divider()

section(
    "Isolation trace",
    "Each row records how the context state changes at each agent step and what isolation action was taken.",
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=340,
)

st.divider()

section(
    "Isolation strategy comparison",
    "This table compares no isolation, late verification, CASCADE isolation, and rollback for the selected scenario.",
)

st.dataframe(
    build_strategy_comparison(scenario),
    use_container_width=True,
    hide_index=True,
    height=240,
)

st.divider()

section(
    "Engineering interpretation",
    "CASCADE Isolation acts like a semantic circuit breaker for multi-agent systems. Instead of allowing a risky claim, unsafe instruction, or unsupported success declaration to move downstream, the system marks the context as contaminated, quarantines it, and resumes from a trusted or sanitized state.",
)