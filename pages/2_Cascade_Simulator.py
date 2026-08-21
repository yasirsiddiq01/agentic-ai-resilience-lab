import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from src.engine import execute_scenario
from src.scenarios import load_scenarios
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
    page_title="Cascade Simulator",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


# ---------------------------------------------------------------------
# Canonical data
# ---------------------------------------------------------------------

AGENTS = list(get_workflow_stages())
SCENARIOS = get_scenario_catalog()

SPEC_REGISTRY = load_scenarios()

SPEC_BY_ID = {
    scenario["id"]: scenario
    for scenario in SPEC_REGISTRY["scenarios"]
}

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
    "clean": "#38bdf8",
    "fault seed": "#ef4444",
    "contaminated": "#f97316",
    "contained": "#facc15",
    "protected": "#22c55e",
    "recovered": "#22c55e",
}


# ---------------------------------------------------------------------
# Canonical cascade view
# ---------------------------------------------------------------------

def build_trace(
    scenario: str,
) -> pd.DataFrame:
    """
    Build presentation rows from the canonical execution trace.

    This page does not simulate scenario behaviour itself.
    """

    scenario_id = SCENARIOS[
        scenario
    ]["scenario_id"]

    return pd.DataFrame(
        get_trace_rows(
            scenario_id
        )
    )


def get_execution(
    scenario: str,
):
    scenario_id = SCENARIOS[
        scenario
    ]["scenario_id"]

    return execute_scenario(
        scenario_id
    )


def get_spec(
    scenario: str,
) -> dict:
    scenario_id = SCENARIOS[
        scenario
    ]["scenario_id"]

    return SPEC_BY_ID[
        scenario_id
    ]


def display_status_for_agent(
    df: pd.DataFrame,
    agent: str,
) -> str:
    """
    Collapse potentially repeated canonical trace entries into one
    visual status for the workflow topology.

    Fault and contamination states take precedence so the original
    propagation path remains visible even after rollback/re-execution.
    """

    rows = df.loc[
        df["agent"] == agent
    ]

    if rows.empty:
        return "pending"

    statuses = set(
        rows["status"].tolist()
    )

    if "fault seed" in statuses:
        return "fault seed"

    if "warning" in statuses:
        return "contaminated"

    if (
        "blocked" in statuses
        or "escalated" in statuses
        or "contained" in statuses
    ):
        return "contained"

    if "evidence" in statuses:
        return "recovered"

    if "normal" in statuses:
        return "clean"

    return "clean"


def animation_stop_index(
    scenario: str,
) -> int:
    """
    Determine how far the replay runner travels.

    Recovered scenarios complete their deterministic re-execution,
    while terminal containment scenarios stop at the control point.
    """

    result = get_execution(
        scenario
    )

    if result.final_state == "RECOVERED":
        return len(AGENTS) - 1

    if result.containment_point is None:
        return len(AGENTS) - 1

    return AGENTS.index(
        result.containment_point
    )


# ---------------------------------------------------------------------
# Workflow SVG
# ---------------------------------------------------------------------

def build_svg_path(
    stop_index: int,
) -> str:
    selected_agents = AGENTS[
        : stop_index + 1
    ]

    commands = []

    for index, agent in enumerate(
        selected_agents
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


def build_cascade_replay_html(
    df: pd.DataFrame,
    scenario: str,
    animate: bool,
) -> str:
    result = get_execution(
        scenario
    )

    stop_index = animation_stop_index(
        scenario
    )

    motion_path = build_svg_path(
        stop_index
    )

    duration = max(
        3.0,
        (stop_index + 1) * 0.55,
    )

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

        status = display_status_for_agent(
            df,
            agent,
        )

        final_color = STATUS_COLORS.get(
            status,
            "#94a3b8",
        )

        if index <= stop_index:
            begin_time = (
                index * 0.55
            )

        else:
            begin_time = (
                duration + 0.35
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
        stop_agent = AGENTS[
            stop_index
        ]

        stop_x, stop_y = SVG_POSITIONS[
            stop_agent
        ]

        runner_path = f"""
            <path
                d="{motion_path}"
                fill="none"
                stroke="rgba(56,189,248,0.95)"
                stroke-width="5"
                stroke-linecap="round"
            />

            <circle
                cx="{stop_x}"
                cy="{stop_y}"
                r="10"
                fill="#ffffff"
                stroke="#38bdf8"
                stroke-width="5"
                class="runner"
            />
        """

    containment = (
        result.containment_point
        if result.containment_point
        is not None
        else "None"
    )

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
                    rgba(148,163,184,0.18);
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
                filter:
                    drop-shadow(
                        0 0 8px
                        rgba(56,189,248,0.85)
                    );
            }}
        </style>
    </head>

    <body>
        <div class="graph-card">

            <div class="title-row">

                <div class="title">
                    Canonical cascade replay
                </div>

                <div class="status">
                    Final state:
                    {html.escape(result.final_state)}
                    |
                    Containment:
                    {html.escape(containment)}
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
# Presentation-only indicator chart
# ---------------------------------------------------------------------

def build_indicator_chart(
    df: pd.DataFrame,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["step"],
            y=df["risk_score"],
            mode="lines+markers",
            text=df["agent"],
            hovertemplate=(
                "<b>%{text}</b>"
                "<br>Trace step %{x}"
                "<br>UI indicator: %{y}"
                "<extra></extra>"
            ),
            line=dict(
                width=3,
            ),
            marker=dict(
                size=9,
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
            title="Canonical trace step",
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
# Canonical comparison
# ---------------------------------------------------------------------

def build_comparison_table() -> pd.DataFrame:
    rows = []

    for display_name, metadata in SCENARIOS.items():
        scenario_id = metadata[
            "scenario_id"
        ]

        spec = SPEC_BY_ID[
            scenario_id
        ]

        result = execute_scenario(
            scenario_id
        )

        rows.append(
            {
                "scenario": display_name,
                "fault_source": (
                    spec["fault_source"]
                    if spec["fault_source"]
                    is not None
                    else "None"
                ),
                "control": spec[
                    "selected_control"
                ],
                "blast_radius": (
                    result.blast_radius
                ),
                "propagation_depth": (
                    result.propagation_depth
                ),
                "containment": (
                    result.containment_point
                    if result.containment_point
                    is not None
                    else "None"
                ),
                "control_response": (
                    result.control_response
                ),
                "final_state": (
                    result.final_state
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ---------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------

page_header(
    "Cascade Simulator",
    (
        "A visual analysis of deterministic failure propagation "
        "in the frozen v1.0 workflow. Blast radius, propagation "
        "depth, containment, and final state come directly from "
        "the canonical execution engine."
    ),
)


scenario_options = list(
    SCENARIOS.keys()
)


if (
    "cascade_scenario"
    not in st.session_state
    or
    st.session_state.cascade_scenario
    not in scenario_options
):
    st.session_state.cascade_scenario = (
        scenario_options[0]
    )


if (
    "cascade_animate_now"
    not in st.session_state
):
    st.session_state.cascade_animate_now = (
        False
    )


left, right = st.columns(
    [1, 1.7]
)


with left:
    st.markdown(
        "### Scenario control"
    )

    selected_scenario = st.selectbox(
        "Frozen v1.0 scenario",
        scenario_options,
        index=scenario_options.index(
            st.session_state.cascade_scenario
        ),
    )

    if st.button(
        "Run cascade replay",
        use_container_width=True,
    ):
        st.session_state.cascade_scenario = (
            selected_scenario
        )

        st.session_state.cascade_animate_now = (
            True
        )

        st.rerun()


scenario = (
    st.session_state.cascade_scenario
)

scenario_id = SCENARIOS[
    scenario
]["scenario_id"]

spec = get_spec(
    scenario
)

result = get_execution(
    scenario
)

df = build_trace(
    scenario
)


fault_source = (
    spec["fault_source"]
    if spec["fault_source"]
    is not None
    else "None"
)

containment = (
    result.containment_point
    if result.containment_point
    is not None
    else "None"
)


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
            f"**Fault source:** {fault_source}"
        )

        st.markdown(
            (
                "**Frozen control:** "
                f"`{spec['selected_control']}`"
            )
        )

        st.markdown(
            (
                "**Control response:** "
                f"`{result.control_response}`"
            )
        )

        st.markdown(
            (
                "**Final state:** "
                f"`{result.final_state}`"
            )
        )

        st.caption(
            (
                "Canonical v1.0 execution. "
                "This page does not define "
                "a separate simulation."
            )
        )


with right:
    st.markdown(
        "### Cascade replay"
    )

    components.html(
        build_cascade_replay_html(
            df=df,
            scenario=scenario,
            animate=(
                st.session_state.cascade_animate_now
            ),
        ),
        height=430,
        scrolling=False,
    )

    st.markdown(
        "### Propagation interpretation"
    )

    with st.container(
        border=True
    ):
        st.write(
            SCENARIOS[
                scenario
            ]["objective"]
        )

        st.markdown(
            (
                "**Fault reaches:** "
                + (
                    ", ".join(
                        result.fault_reaches
                    )
                    if result.fault_reaches
                    else "None"
                )
            )
        )

        st.markdown(
            (
                "**Containment point:** "
                f"{containment}"
            )
        )

        if result.rollback_to:
            st.markdown(
                (
                    "**Rollback target:** "
                    f"{result.rollback_to}"
                )
            )


if (
    st.session_state.cascade_animate_now
):
    st.session_state.cascade_animate_now = (
        False
    )


st.success(
    (
        f"{scenario_id}: "
        f"{result.final_state}. "
        f"Blast radius: "
        f"{result.blast_radius}. "
        f"Propagation depth: "
        f"{result.propagation_depth}."
    )
)


# ---------------------------------------------------------------------
# Canonical metrics
# ---------------------------------------------------------------------

m1, m2, m3, m4 = st.columns(
    4
)


with m1:
    metric_card(
        "Fault source",
        fault_source,
        "Frozen scenario specification",
    )


with m2:
    metric_card(
        "Blast radius",
        str(
            result.blast_radius
        ),
        "Canonical downstream reach",
    )


with m3:
    metric_card(
        "Propagation depth",
        str(
            result.propagation_depth
        ),
        "Canonical propagation metric",
    )


with m4:
    metric_card(
        "Containment",
        containment,
        "Canonical control point",
    )


# ---------------------------------------------------------------------
# Indicator chart
# ---------------------------------------------------------------------

st.divider()


section(
    "Trace indicator",
    (
        "The line is a presentation-only heuristic mapped onto "
        "canonical trace states. Blast radius and propagation "
        "depth above are canonical engine metrics; this indicator "
        "is not a calibrated probability or risk model."
    ),
)


st.plotly_chart(
    build_indicator_chart(
        df
    ),
    use_container_width=True,
    config={
        "displayModeBar": False,
    },
)


# ---------------------------------------------------------------------
# Canonical trace
# ---------------------------------------------------------------------

st.divider()


section(
    "Canonical propagation trace",
    (
        "Every row below originates from the deterministic v1.0 "
        "execution trace. No page-local propagation decisions "
        "are generated here."
    ),
)


st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=380,
)


# ---------------------------------------------------------------------
# Scenario comparison
# ---------------------------------------------------------------------

st.divider()


section(
    "Frozen scenario comparison",
    (
        "Comparison of all eight v1.0 scenarios using the "
        "authoritative engine outputs."
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
        "The Cascade Simulator is now a visual analysis layer. "
        "Fault propagation, containment, recovery, blast radius, "
        "and propagation depth are determined by src.engine and "
        "the frozen scenario registry rather than by Streamlit "
        "page logic."
    ),
)