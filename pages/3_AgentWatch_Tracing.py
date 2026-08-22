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
    get_workflow_stages,
)


st.set_page_config(
    page_title="AgentWatch Tracing",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


# ---------------------------------------------------------------------
# Canonical data
# ---------------------------------------------------------------------

AGENTS = list(
    get_workflow_stages()
)

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
    "PROCESSED": "#38bdf8",
    "FAULT_SOURCE": "#ef4444",
    "CONTAMINATED": "#f97316",
    "BLOCK": "#facc15",
    "ESCALATE": "#f97316",
    "REQUIRE_HUMAN_APPROVAL": "#f97316",
    "NOT_EXECUTED": "#22c55e",
    "ISOLATED": "#facc15",
    "PROTECTED": "#22c55e",
    "ROLLBACK_TRIGGERED": "#facc15",
    "RESTORED": "#22c55e",
    "REEXECUTED": "#22c55e",
    "pending": "#475569",
}


STATUS_LABELS = {
    "PROCESSED": "processed",
    "FAULT_SOURCE": "fault source",
    "CONTAMINATED": "contaminated",
    "BLOCK": "blocked",
    "ESCALATE": "escalated",
    "REQUIRE_HUMAN_APPROVAL": "human approval",
    "NOT_EXECUTED": "protected",
    "ISOLATED": "isolated",
    "PROTECTED": "protected",
    "ROLLBACK_TRIGGERED": "rollback",
    "RESTORED": "restored",
    "REEXECUTED": "re-executed",
}


# Presentation-only indicator.
# This is not a probability, confidence score, or calibrated risk model.
TRACE_INDICATOR = {
    "PROCESSED": 0.10,
    "FAULT_SOURCE": 0.90,
    "CONTAMINATED": 0.80,
    "BLOCK": 0.75,
    "ESCALATE": 0.70,
    "REQUIRE_HUMAN_APPROVAL": 0.70,
    "NOT_EXECUTED": 0.20,
    "ISOLATED": 0.30,
    "PROTECTED": 0.15,
    "ROLLBACK_TRIGGERED": 0.40,
    "RESTORED": 0.20,
    "REEXECUTED": 0.15,
}


# ---------------------------------------------------------------------
# Canonical execution helpers
# ---------------------------------------------------------------------

def get_scenario_id(
    scenario: str,
) -> str:
    return SCENARIOS[
        scenario
    ]["scenario_id"]


def get_spec(
    scenario: str,
) -> dict:
    scenario_id = get_scenario_id(
        scenario
    )

    return SPEC_BY_ID[
        scenario_id
    ]


def get_execution(
    scenario: str,
):
    return execute_scenario(
        get_scenario_id(
            scenario
        )
    )


def build_trace(
    scenario: str,
) -> pd.DataFrame:
    """
    Convert authoritative TraceRecord objects into a DataFrame.

    No scenario behaviour or trace events are defined in this page.
    """

    result = get_execution(
        scenario
    )

    rows = []

    for record in result.trace:
        rows.append(
            {
                "step": record.step,
                "workflow_stage": (
                    record.workflow_stage
                ),
                "input_source": (
                    record.input_source
                ),
                "event": record.event,
                "evidence_state": (
                    record.evidence_state
                ),
                "context_state": (
                    record.context_state
                ),
                "failure_label": (
                    record.failure_label
                ),
                "control_response": (
                    record.control_response
                ),
                "status": record.status,
                "ui_indicator": (
                    TRACE_INDICATOR.get(
                        record.status,
                        0.10,
                    )
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


# ---------------------------------------------------------------------
# Workflow topology
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


def visual_status_for_stage(
    df: pd.DataFrame,
    agent: str,
) -> str:
    """
    Choose one visual state when a stage appears multiple times.

    Fault/contamination remain visible even when a recovery scenario
    subsequently re-executes the stage.
    """

    rows = df.loc[
        df["workflow_stage"]
        == agent
    ]

    if rows.empty:
        return "pending"

    statuses = set(
        rows["status"].tolist()
    )

    precedence = [
        "FAULT_SOURCE",
        "CONTAMINATED",
        "ROLLBACK_TRIGGERED",
        "ISOLATED",
        "BLOCK",
        "ESCALATE",
        "REQUIRE_HUMAN_APPROVAL",
        "RESTORED",
        "REEXECUTED",
        "PROTECTED",
        "NOT_EXECUTED",
        "PROCESSED",
    ]

    for status in precedence:
        if status in statuses:
            return status

    return rows.iloc[-1][
        "status"
    ]


def build_agentwatch_replay_html(
    df: pd.DataFrame,
    scenario: str,
    animate: bool,
) -> str:
    """
    Render canonical trace topology.

    The SVG is presentation only; its states come from TraceRecord.
    """

    result = get_execution(
        scenario
    )

    spec = get_spec(
        scenario
    )

    motion_path = build_svg_path()

    duration = 4.8

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

        status = visual_status_for_stage(
            df,
            agent,
        )

        final_color = STATUS_COLORS.get(
            status,
            "#94a3b8",
        )

        label = STATUS_LABELS.get(
            status,
            status.lower(),
        )

        begin_time = (
            index * 0.55
        )

        safe_agent = html.escape(
            agent
        )

        safe_label = html.escape(
            label
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
                    {safe_label}
                </text>
            </g>
            """
        )

    if animate:
        runner = f"""
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
        runner = f"""
            <path
                d="{motion_path}"
                fill="none"
                stroke="rgba(56,189,248,0.95)"
                stroke-width="5"
                stroke-linecap="round"
            />
        """

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
                background: rgba(15,23,42,0.55);
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
                    Canonical trace replay
                </div>

                <div class="status">
                    Fault source:
                    {html.escape(fault_source)}
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
                {runner}
                {"".join(node_items)}
            </svg>

        </div>
    </body>
    </html>
    """


# ---------------------------------------------------------------------
# Trace indicator
# ---------------------------------------------------------------------

def build_trace_chart(
    df: pd.DataFrame,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["step"],
            y=df["ui_indicator"],
            mode=(
                "lines+markers+text"
            ),
            text=df[
                "workflow_stage"
            ],
            textposition=(
                "top center"
            ),
            line=dict(
                width=3,
            ),
            marker=dict(
                size=9,
            ),
            hovertemplate=(
                "<b>%{text}</b>"
                "<br>Trace event %{x}"
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
            title="Canonical trace event",
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
# Trace-state counts
# ---------------------------------------------------------------------

def build_status_counts(
    df: pd.DataFrame,
) -> pd.DataFrame:
    counts = (
        df["status"]
        .value_counts()
        .rename_axis(
            "canonical_status"
        )
        .reset_index(
            name="event_count"
        )
    )

    return counts


# ---------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------

page_header(
    "AgentWatch Tracing",
    (
        "Deterministic trace inspection for the frozen v1.0 "
        "multi-stage workflow. The page displays canonical "
        "TraceRecord events emitted by the execution engine; "
        "it is not runtime instrumentation of live agents."
    ),
)


scenario_options = list(
    SCENARIOS.keys()
)


if (
    "agentwatch_scenario"
    not in st.session_state
    or
    st.session_state.agentwatch_scenario
    not in scenario_options
):
    st.session_state.agentwatch_scenario = (
        scenario_options[0]
    )


if (
    "agentwatch_animate_now"
    not in st.session_state
):
    st.session_state.agentwatch_animate_now = (
        False
    )


left, right = st.columns(
    [1, 1.7]
)


with left:
    st.markdown(
        "### Trace control"
    )

    selected_scenario = st.selectbox(
        "Frozen v1.0 scenario",
        scenario_options,
        index=scenario_options.index(
            st.session_state.agentwatch_scenario
        ),
    )

    if st.button(
        "Replay canonical trace",
        use_container_width=True,
    ):
        st.session_state.agentwatch_scenario = (
            selected_scenario
        )

        st.session_state.agentwatch_animate_now = (
            True
        )

        st.rerun()


scenario = (
    st.session_state.agentwatch_scenario
)

scenario_id = get_scenario_id(
    scenario
)

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

failure_label = (
    spec["fault_type"]
    if spec["fault_type"]
    != "NONE"
    else "None"
)


with left:
    with st.container(
        border=True
    ):
        st.markdown(
            "### Active trace"
        )

        st.markdown(
            f"**Scenario:** {scenario}"
        )

        st.markdown(
            (
                "**Fault source:** "
                f"{fault_source}"
            )
        )

        st.markdown(
            (
                "**Failure label:** "
                f"`{failure_label}`"
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
                "Synthetic deterministic trace "
                "from the canonical v1.0 engine."
            )
        )


with right:
    st.markdown(
        "### Trace replay"
    )

    components.html(
        build_agentwatch_replay_html(
            df=df,
            scenario=scenario,
            animate=(
                st.session_state.agentwatch_animate_now
            ),
        ),
        height=430,
        scrolling=False,
    )

    st.markdown(
        "### Trace diagnosis"
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
                "**Containment:** "
                f"{containment}"
            )
        )

        st.markdown(
            (
                "**Control response:** "
                f"`{result.control_response}`"
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
    st.session_state.agentwatch_animate_now
):
    st.session_state.agentwatch_animate_now = (
        False
    )


st.success(
    (
        f"{scenario_id}: "
        f"{len(df)} canonical trace events. "
        f"Final state: {result.final_state}."
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
        "Trace events",
        str(
            len(df)
        ),
        "Canonical TraceRecord count",
    )


with m2:
    metric_card(
        "Fault source",
        fault_source,
        "Frozen scenario specification",
    )


with m3:
    metric_card(
        "Blast radius",
        str(
            result.blast_radius
        ),
        "Canonical propagation reach",
    )


with m4:
    metric_card(
        "Containment",
        containment,
        "Canonical control point",
    )


# ---------------------------------------------------------------------
# Trace indicator
# ---------------------------------------------------------------------

st.divider()


section(
    "Trace-state indicator",
    (
        "A fixed presentation-only heuristic mapped to canonical "
        "TraceRecord statuses. It is not a probability, classifier "
        "confidence, or calibrated risk estimate."
    ),
)


st.plotly_chart(
    build_trace_chart(
        df
    ),
    use_container_width=True,
    config={
        "displayModeBar": False,
    },
)


# ---------------------------------------------------------------------
# Canonical trace table
# ---------------------------------------------------------------------

st.divider()


section(
    "Canonical trace records",
    (
        "These rows are emitted directly by src.engine as "
        "TraceRecord objects. The table preserves input source, "
        "event, evidence state, context state, failure label, "
        "control response, and execution status."
    ),
)


st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=420,
)


# ---------------------------------------------------------------------
# Status summary
# ---------------------------------------------------------------------

st.divider()


section(
    "Trace-state summary",
    (
        "Counts of canonical execution statuses in the selected "
        "scenario. Re-execution and restoration events remain "
        "separate rather than being collapsed into an invented "
        "single trace state."
    ),
)


st.dataframe(
    build_status_counts(
        df
    ),
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------------------
# Claim boundary
# ---------------------------------------------------------------------

st.divider()


section(
    "Observability boundary",
    (
        "AgentWatch in v1.0 is deterministic synthetic trace "
        "inspection. It demonstrates trace structure and visibility "
        "of propagation, containment, and recovery events. It does "
        "not claim live-agent telemetry, production instrumentation, "
        "or monitoring of deployed autonomous systems."
    ),
)