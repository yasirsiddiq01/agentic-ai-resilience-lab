import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from src.ui import (
    apply_global_style,
    metric_card,
    page_header,
    section,
)
from src.ui_adapter import (
    get_scenario_catalog,
    get_trace_rows,
    get_workflow_stages,
)


st.set_page_config(
    page_title="Enterprise Incident Workflow",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


# ---------------------------------------------------------------------
# Canonical data
# ---------------------------------------------------------------------

AGENTS = list(get_workflow_stages())

SCENARIOS = get_scenario_catalog()

EDGES = list(
    zip(
        AGENTS,
        AGENTS[1:],
    )
)


# ---------------------------------------------------------------------
# Presentation configuration
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# Canonical-engine adapter
# ---------------------------------------------------------------------

def build_trace(
    scenario: str,
) -> pd.DataFrame:
    """
    Convert canonical execution records into the table format used
    by this Streamlit presentation layer.

    Scenario behaviour itself is not defined in this page.
    """

    scenario_id = SCENARIOS[
        scenario
    ]["scenario_id"]

    return pd.DataFrame(
        get_trace_rows(
            scenario_id
        )
    )


# ---------------------------------------------------------------------
# Workflow replay
# ---------------------------------------------------------------------

def build_svg_path() -> str:
    commands = []

    for index, agent in enumerate(
        AGENTS
    ):
        x, y = SVG_POSITIONS[
            agent
        ]

        if index == 0:
            commands.append(
                f"M {x} {y}"
            )
        else:
            commands.append(
                f"L {x} {y}"
            )

    return " ".join(
        commands
    )


def build_workflow_replay_html(
    df: pd.DataFrame,
    scenario: str,
    animate: bool,
) -> str:
    """
    Build the existing workflow SVG using canonical engine output.
    """

    motion_path = build_svg_path()

    duration = 4.8

    summary = SCENARIOS[
        scenario
    ]

    edge_lines = []

    for source, target in EDGES:
        x1, y1 = SVG_POSITIONS[
            source
        ]

        x2, y2 = SVG_POSITIONS[
            target
        ]

        edge_lines.append(
            f"""
            <line
                x1="{x1}"
                y1="{y1}"
                x2="{x2}"
                y2="{y2}"
                stroke="rgba(148,163,184,0.40)"
                stroke-width="3"
            />
            """
        )

    node_items = []

    for index, agent in enumerate(
        AGENTS
    ):
        x, y = SVG_POSITIONS[
            agent
        ]

        agent_rows = df.loc[
            df["agent"] == agent
        ]

        if agent_rows.empty:
            status = "pending"

        else:
            # Some recovery scenarios revisit workflow stages.
            # The graph shows the final state recorded for each stage.
            status = agent_rows.iloc[
                -1
            ]["status"]

        final_color = (
            STATUS_COLORS.get(
                status,
                "#94a3b8",
            )
        )

        begin_time = (
            index * 0.55
        )

        safe_agent = html.escape(
            agent
        )

        safe_status = html.escape(
            status
        )

        if animate:
            circle = f"""
                <circle
                    cx="{x}"
                    cy="{y}"
                    r="19"
                    fill="{STATUS_COLORS['pending']}"
                    stroke="rgba(248,250,252,0.85)"
                    stroke-width="3"
                >
                    <animate
                        attributeName="fill"
                        from="{STATUS_COLORS['pending']}"
                        to="{final_color}"
                        begin="{begin_time}s"
                        dur="0.22s"
                        fill="freeze"
                    />
                </circle>
            """

            pulse = f"""
                <circle
                    cx="{x}"
                    cy="{y}"
                    r="25"
                    fill="none"
                    stroke="{final_color}"
                    stroke-width="2"
                    opacity="0"
                >
                    <animate
                        attributeName="opacity"
                        values="0;0.85;0"
                        begin="{begin_time}s"
                        dur="0.65s"
                        fill="freeze"
                    />

                    <animate
                        attributeName="r"
                        values="21;31;25"
                        begin="{begin_time}s"
                        dur="0.65s"
                        fill="freeze"
                    />
                </circle>
            """

        else:
            circle = f"""
                <circle
                    cx="{x}"
                    cy="{y}"
                    r="19"
                    fill="{final_color}"
                    stroke="rgba(248,250,252,0.85)"
                    stroke-width="3"
                />
            """

            pulse = ""

        node_items.append(
            f"""
            <g>
                {circle}
                {pulse}

                <text
                    x="{x}"
                    y="{y + 43}"
                    text-anchor="middle"
                    fill="#e5e7eb"
                    font-size="13"
                    font-weight="600"
                >
                    {safe_agent}
                </text>

                <text
                    x="{x}"
                    y="{y + 60}"
                    text-anchor="middle"
                    fill="#94a3b8"
                    font-size="11"
                >
                    {safe_status}
                </text>
            </g>
            """
        )

    if animate:
        runner_path = f"""
            <path
                d="{motion_path}"
                fill="none"
                stroke="rgba(56,189,248,0.95)"
                stroke-width="5"
                stroke-linecap="round"
                stroke-dasharray="1200"
                stroke-dashoffset="1200"
            >
                <animate
                    attributeName="stroke-dashoffset"
                    from="1200"
                    to="0"
                    dur="{duration}s"
                    fill="freeze"
                />
            </path>

            <circle
                r="10"
                fill="#ffffff"
                stroke="#38bdf8"
                stroke-width="5"
                class="runner"
            >
                <animateMotion
                    dur="{duration}s"
                    path="{motion_path}"
                    fill="freeze"
                    calcMode="linear"
                />
            </circle>
        """

    else:
        runner_path = f"""
            <path
                d="{motion_path}"
                fill="none"
                stroke="rgba(56,189,248,0.95)"
                stroke-width="5"
                stroke-linecap="round"
            />

            <circle
                cx="{SVG_POSITIONS['Report Agent'][0]}"
                cy="{SVG_POSITIONS['Report Agent'][1]}"
                r="10"
                fill="#ffffff"
                stroke="#38bdf8"
                stroke-width="5"
                class="runner"
            />
        """

    return f"""
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
                border:
                    1px solid
                    rgba(148, 163, 184, 0.18);
                padding: 12px;
                box-sizing: border-box;
            }}

            .title-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: #e5e7eb;
                padding:
                    0 10px 4px 10px;
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
                filter:
                    drop-shadow(
                        0 0 8px
                        rgba(
                            56,
                            189,
                            248,
                            0.85
                        )
                    );
            }}
        </style>
    </head>

    <body>
        <div class="graph-card">

            <div class="title-row">
                <div class="title">
                    Enterprise incident replay
                </div>

                <div class="status">
                    Scenario:
                    {html.escape(scenario)}
                    |
                    Containment:
                    {html.escape(summary["containment"])}
                </div>
            </div>

            <svg
                viewBox="0 0 900 330"
                width="100%"
                height="390"
            >
                {"".join(edge_lines)}
                {runner_path}
                {"".join(node_items)}
            </svg>

        </div>
    </body>
    </html>
    """


# ---------------------------------------------------------------------
# Presentation-only risk indicator
# ---------------------------------------------------------------------

def build_risk_chart(
    df: pd.DataFrame,
) -> go.Figure:
    """
    Visualise a fixed UI heuristic.

    This is not a calibrated risk estimate.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["step"],
            y=df["risk_score"],
            mode=(
                "lines+markers+text"
            ),
            text=df["agent"],
            textposition=(
                "top center"
            ),
            line=dict(
                width=3,
            ),
            marker=dict(
                size=10,
            ),
            hovertemplate=(
                "<b>%{text}</b>"
                "<br>Trace step %{x}"
                "<br>UI indicator: %{y}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=340,
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),
        plot_bgcolor=(
            "rgba(15,23,42,0.55)"
        ),
        font=dict(
            color="#e5e7eb",
        ),
        xaxis=dict(
            title="Trace step",
            gridcolor=(
                "rgba(148,163,184,0.15)"
            ),
            dtick=1,
        ),
        yaxis=dict(
            title=(
                "UI heuristic indicator"
            ),
            range=[0, 1],
            gridcolor=(
                "rgba(148,163,184,0.15)"
            ),
        ),
    )

    return fig


# ---------------------------------------------------------------------
# Scenario comparison
# ---------------------------------------------------------------------

def build_comparison_table() -> pd.DataFrame:
    rows = []

    for scenario in SCENARIOS:
        trace = build_trace(
            scenario
        )

        rows.append(
            {
                "scenario": scenario,
                "fault_source": (
                    SCENARIOS[
                        scenario
                    ]["root_cause"]
                ),
                "containment": (
                    SCENARIOS[
                        scenario
                    ]["containment"]
                ),
                "final_state": (
                    SCENARIOS[
                        scenario
                    ]["final_state"]
                ),
                "max_indicator": round(
                    trace[
                        "risk_score"
                    ].max(),
                    2,
                ),
                "high_indicator_steps": int(
                    (
                        trace[
                            "risk_score"
                        ]
                        >= 0.70
                    ).sum()
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ---------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------

page_header(
    "Enterprise Incident Workflow",
    (
        "A deterministic enterprise-style incident workflow "
        "showing canonical handoffs, evidence states, "
        "containment controls, and recovery behaviour."
    ),
)


# ---------------------------------------------------------------------
# Scenario state
# ---------------------------------------------------------------------

scenario_options = list(
    SCENARIOS.keys()
)


# Reset stale legacy values stored by Streamlit.
if (
    "workflow_scenario"
    not in st.session_state
    or
    st.session_state.workflow_scenario
    not in scenario_options
):
    st.session_state.workflow_scenario = (
        scenario_options[0]
    )


if (
    "workflow_animate_now"
    not in st.session_state
):
    st.session_state.workflow_animate_now = (
        False
    )


# ---------------------------------------------------------------------
# Scenario controls and replay
# ---------------------------------------------------------------------

left, right = st.columns(
    [1, 1.7]
)


with left:
    st.markdown(
        "### Scenario control"
    )

    selected_scenario = st.selectbox(
        "Select workflow condition",
        scenario_options,
        index=scenario_options.index(
            st.session_state.workflow_scenario
        ),
    )

    if st.button(
        "Run incident workflow",
        use_container_width=True,
    ):
        st.session_state.workflow_scenario = (
            selected_scenario
        )

        st.session_state.workflow_animate_now = (
            True
        )

        st.rerun()


scenario = (
    st.session_state.workflow_scenario
)

df = build_trace(
    scenario
)

summary = SCENARIOS[
    scenario
]


max_risk = round(
    df["risk_score"].max(),
    2,
)

high_risk_steps = int(
    (
        df["risk_score"] >= 0.70
    ).sum()
)


# ---------------------------------------------------------------------
# Active experiment card
# ---------------------------------------------------------------------

with left:
    with st.container(
        border=True
    ):
        st.markdown(
            "### Active experiment"
        )

        st.markdown(
            f"**Scenario:** {scenario}"
        )

        st.markdown(
            "**Objective:**"
        )

        st.write(
            summary["objective"]
        )

        st.markdown(
            (
                "**Final state:** "
                f"`{summary['final_state']}`"
            )
        )

        st.caption(
            (
                "deterministic workflow "
                "· canonical engine"
            )
        )


# ---------------------------------------------------------------------
# Workflow replay and diagnosis
# ---------------------------------------------------------------------

with right:
    st.markdown(
        "### Workflow replay"
    )

    components.html(
        build_workflow_replay_html(
            df=df,
            scenario=scenario,
            animate=(
                st.session_state.workflow_animate_now
            ),
        ),
        height=430,
        scrolling=False,
    )

    st.markdown(
        "### Scenario diagnosis"
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### {scenario}"
        )

        st.write(
            summary["summary"]
        )

        st.markdown(
            (
                "**Fault source:** "
                f"{summary['root_cause']}"
            )
        )

        st.markdown(
            (
                "**Containment:** "
                f"{summary['containment']}"
            )
        )

        st.markdown(
            (
                "**Final state:** "
                f"`{summary['final_state']}`"
            )
        )


if (
    st.session_state.workflow_animate_now
):
    st.session_state.workflow_animate_now = (
        False
    )


# ---------------------------------------------------------------------
# Current result
# ---------------------------------------------------------------------

st.success(
    (
        f"Active workflow: {scenario}. "
        f"Final state: "
        f"{summary['final_state']}. "
        f"Containment: "
        f"{summary['containment']}."
    )
)


# ---------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------

m1, m2, m3, m4 = st.columns(
    4
)


with m1:
    metric_card(
        "Fault source",
        summary["root_cause"],
        "First injected abnormal source",
    )


with m2:
    metric_card(
        "Containment",
        summary["containment"],
        "Canonical control point",
    )


with m3:
    metric_card(
        "Max risk indicator",
        str(max_risk),
        "Presentation-only heuristic",
    )


with m4:
    metric_card(
        "High-indicator steps",
        str(high_risk_steps),
        "UI heuristic ≥ 0.70",
    )


# ---------------------------------------------------------------------
# Risk-indicator chart
# ---------------------------------------------------------------------

st.divider()


section(
    "Risk indicator over workflow",
    (
        "A fixed presentation-only heuristic used to "
        "visualise the canonical execution trace. "
        "It is not a calibrated risk model."
    ),
)


st.plotly_chart(
    build_risk_chart(
        df
    ),
    use_container_width=True,
    config={
        "displayModeBar": False,
    },
)


# ---------------------------------------------------------------------
# Execution trace
# ---------------------------------------------------------------------

st.divider()


section(
    "Execution trace",
    (
        "Each row is produced from the canonical deterministic "
        "execution engine and records evidence state, context "
        "state, control response, and presentation status."
    ),
)


st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=380,
)


# ---------------------------------------------------------------------
# Experiment comparison
# ---------------------------------------------------------------------

st.divider()


section(
    "Experiment comparison",
    (
        "This table compares all eight frozen v1.0 "
        "scenarios using canonical engine output."
    ),
)


st.dataframe(
    build_comparison_table(),
    use_container_width=True,
    hide_index=True,
    height=320,
)


# ---------------------------------------------------------------------
# Interpretation
# ---------------------------------------------------------------------

st.divider()


section(
    "Engineering interpretation",
    (
        "This page is a visualisation layer over the canonical "
        "v1.0 deterministic simulation. Scenario behaviour is "
        "defined by the frozen scenario registry and execution "
        "engine rather than by page-local simulation logic."
    ),
)