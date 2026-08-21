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
    get_workflow_stages,
)


st.set_page_config(
    page_title="CASCADE Isolation",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


# ---------------------------------------------------------------------
# Canonical workflow and frozen CASCADE scenarios
# ---------------------------------------------------------------------

AGENTS = list(
    get_workflow_stages()
)

SCENARIO_REGISTRY = load_scenarios()

SCENARIOS_BY_ID = {
    scenario["id"]: scenario
    for scenario in SCENARIO_REGISTRY["scenarios"]
}


CASCADE_SCENARIO_IDS = (
    "S05",
    "S08",
)


CASCADE_SCENARIOS = {
    (
        f"{scenario_id} — "
        f"{SCENARIOS_BY_ID[scenario_id]['name']}"
    ): scenario_id
    for scenario_id in CASCADE_SCENARIO_IDS
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
    "ISOLATED": "#facc15",
    "PROTECTED": "#22c55e",
    "ROLLBACK_TRIGGERED": "#facc15",
    "RESTORED": "#22c55e",
    "REEXECUTED": "#22c55e",
    "NOT_EXECUTED": "#22c55e",
    "pending": "#475569",
}


STATUS_LABELS = {
    "PROCESSED": "trusted",
    "FAULT_SOURCE": "fault source",
    "CONTAMINATED": "contaminated",
    "ISOLATED": "isolated",
    "PROTECTED": "protected",
    "ROLLBACK_TRIGGERED": "rollback",
    "RESTORED": "restored",
    "REEXECUTED": "re-executed",
    "NOT_EXECUTED": "protected",
}


TRACE_INDICATOR = {
    "PROCESSED": 0.10,
    "FAULT_SOURCE": 0.90,
    "CONTAMINATED": 0.80,
    "ISOLATED": 0.30,
    "PROTECTED": 0.15,
    "ROLLBACK_TRIGGERED": 0.40,
    "RESTORED": 0.20,
    "REEXECUTED": 0.15,
    "NOT_EXECUTED": 0.15,
}


# ---------------------------------------------------------------------
# Canonical helpers
# ---------------------------------------------------------------------

def get_scenario_id(
    display_name: str,
) -> str:
    return CASCADE_SCENARIOS[
        display_name
    ]


def get_spec(
    display_name: str,
) -> dict:
    scenario_id = get_scenario_id(
        display_name
    )

    return SCENARIOS_BY_ID[
        scenario_id
    ]


def get_execution(
    display_name: str,
):
    return execute_scenario(
        get_scenario_id(
            display_name
        )
    )


def build_trace(
    display_name: str,
) -> pd.DataFrame:
    """
    Build the page directly from canonical TraceRecord events.

    No isolation, quarantine, rollback, or re-execution behaviour
    is simulated in this page.
    """

    result = get_execution(
        display_name
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
# Visual topology
# ---------------------------------------------------------------------

def visual_status_for_stage(
    df: pd.DataFrame,
    agent: str,
) -> str:
    """
    Select one topology state when recovery revisits a stage.

    Fault and isolation events remain visible even when execution
    later continues with restored or clean context.
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


def build_isolation_replay_html(
    df: pd.DataFrame,
    display_name: str,
    animate: bool,
) -> str:
    result = get_execution(
        display_name
    )

    spec = get_spec(
        display_name
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

        color = STATUS_COLORS.get(
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
                        to="{color}"
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
                    stroke="{color}"
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
                    fill="{color}"
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

    containment = (
        result.containment_point
        if result.containment_point
        is not None
        else "None"
    )

    rollback = (
        result.rollback_to
        if result.rollback_to
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
                font-family:
                    Segoe UI,
                    Arial,
                    sans-serif;
            }}

            .graph-card {{
                width: 100%;
                border-radius: 20px;
                background:
                    rgba(
                        15,
                        23,
                        42,
                        0.55
                    );
                border:
                    1px solid
                    rgba(
                        148,
                        163,
                        184,
                        0.18
                    );
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
        </style>
    </head>

    <body>
        <div class="graph-card">

            <div class="title-row">

                <div class="title">
                    Canonical isolation replay
                </div>

                <div class="status">
                    Control:
                    {html.escape(spec["selected_control"])}
                    |
                    Containment:
                    {html.escape(containment)}
                    |
                    Rollback:
                    {html.escape(rollback)}
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
# Trace indicator chart
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
            title=(
                "Canonical trace event"
            ),
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
# Recovery evidence
# ---------------------------------------------------------------------

def build_control_evidence(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return only isolation/recovery-related canonical trace events.
    """

    relevant_statuses = {
        "ISOLATED",
        "PROTECTED",
        "ROLLBACK_TRIGGERED",
        "RESTORED",
        "REEXECUTED",
    }

    evidence = df.loc[
        df["status"].isin(
            relevant_statuses
        ),
        [
            "step",
            "workflow_stage",
            "event",
            "evidence_state",
            "context_state",
            "control_response",
            "status",
        ],
    ]

    return evidence.reset_index(
        drop=True
    )


# ---------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------

page_header(
    "CASCADE Isolation",
    (
        "Inspection of the frozen v1.0 CASCADE isolation "
        "and rollback scenarios. The page displays canonical "
        "engine events rather than implementing a second "
        "page-local isolation simulation."
    ),
)


scenario_options = list(
    CASCADE_SCENARIOS.keys()
)


if (
    "isolation_scenario"
    not in st.session_state
    or
    st.session_state.isolation_scenario
    not in scenario_options
):
    st.session_state.isolation_scenario = (
        scenario_options[0]
    )


if (
    "isolation_animate_now"
    not in st.session_state
):
    st.session_state.isolation_animate_now = (
        False
    )


left, right = st.columns(
    [1, 1.7]
)


with left:
    st.markdown(
        "### Isolation control"
    )

    selected_scenario = st.selectbox(
        "Frozen CASCADE scenario",
        scenario_options,
        index=scenario_options.index(
            st.session_state.isolation_scenario
        ),
    )

    if st.button(
        "Replay canonical isolation",
        use_container_width=True,
    ):
        st.session_state.isolation_scenario = (
            selected_scenario
        )

        st.session_state.isolation_animate_now = (
            True
        )

        st.rerun()


display_name = (
    st.session_state.isolation_scenario
)

scenario_id = get_scenario_id(
    display_name
)

spec = get_spec(
    display_name
)

result = get_execution(
    display_name
)

df = build_trace(
    display_name
)

control_evidence = (
    build_control_evidence(
        df
    )
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

rollback = (
    result.rollback_to
    if result.rollback_to
    is not None
    else "None"
)


with left:
    with st.container(
        border=True
    ):
        st.markdown(
            "### Active control path"
        )

        st.markdown(
            (
                "**Scenario:** "
                f"{display_name}"
            )
        )

        st.markdown(
            (
                "**Fault source:** "
                f"{fault_source}"
            )
        )

        st.markdown(
            (
                "**Control:** "
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
                "Canonical deterministic execution. "
                "No page-local rollback logic."
            )
        )


with right:
    st.markdown(
        "### Isolation replay"
    )

    components.html(
        build_isolation_replay_html(
            df=df,
            display_name=display_name,
            animate=(
                st.session_state.isolation_animate_now
            ),
        ),
        height=430,
        scrolling=False,
    )

    st.markdown(
        "### Control interpretation"
    )

    with st.container(
        border=True
    ):
        st.write(
            spec["description"]
        )

        st.markdown(
            (
                "**Containment point:** "
                f"{containment}"
            )
        )

        st.markdown(
            (
                "**Rollback target:** "
                f"{rollback}"
            )
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


if (
    st.session_state.isolation_animate_now
):
    st.session_state.isolation_animate_now = (
        False
    )


st.success(
    (
        f"{scenario_id}: "
        f"{result.final_state}. "
        f"Containment: {containment}. "
        f"Rollback: {rollback}."
    )
)


# ---------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------

reexecuted_count = int(
    (
        df["status"]
        == "REEXECUTED"
    ).sum()
)

restored_count = int(
    (
        df["status"]
        == "RESTORED"
    ).sum()
)


m1, m2, m3, m4 = st.columns(
    4
)


with m1:
    metric_card(
        "Blast radius",
        str(
            result.blast_radius
        ),
        "Canonical downstream reach",
    )


with m2:
    metric_card(
        "Containment",
        containment,
        "Canonical isolation point",
    )


with m3:
    metric_card(
        "Rollback target",
        rollback,
        "Last trusted state",
    )


with m4:
    metric_card(
        "Re-executed events",
        str(
            reexecuted_count
        ),
        "Canonical recovery trace",
    )


# ---------------------------------------------------------------------
# Trace chart
# ---------------------------------------------------------------------

st.divider()


section(
    "Isolation and recovery trace",
    (
        "The line is a presentation-only heuristic mapped onto "
        "canonical execution states. Isolation, restoration, "
        "rollback, and re-execution events themselves come "
        "directly from the engine."
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
# Canonical trace
# ---------------------------------------------------------------------

st.divider()


section(
    "Canonical execution trace",
    (
        "The complete deterministic TraceRecord sequence for "
        "the selected frozen CASCADE scenario."
    ),
)


st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=420,
)


# ---------------------------------------------------------------------
# Isolation / rollback evidence
# ---------------------------------------------------------------------

st.divider()


section(
    "Control evidence",
    (
        "Subset of canonical events specifically associated "
        "with isolation, protection, restoration, rollback, "
        "or deterministic re-execution."
    ),
)


st.dataframe(
    control_evidence,
    use_container_width=True,
    hide_index=True,
    height=300,
)


# ---------------------------------------------------------------------
# Recovery interpretation
# ---------------------------------------------------------------------

st.divider()


if scenario_id == "S08":
    section(
        "Recovery interpretation",
        (
            f"The canonical trace contains {restored_count} "
            f"RESTORED event and {reexecuted_count} "
            "REEXECUTED events. This is the bounded v1.0 "
            "simulation of trusted-state restoration and "
            "deterministic continuation after containment."
        ),
    )

else:
    section(
        "Containment interpretation",
        (
            "S05 demonstrates deterministic context isolation "
            "without rollback. The contaminated instruction is "
            "contained at the canonical isolation point and "
            "downstream workflow stages receive protected context."
        ),
    )


# ---------------------------------------------------------------------
# Claim boundary
# ---------------------------------------------------------------------

st.divider()


section(
    "Claim boundary",
    (
        "CASCADE Isolation v1.0 is a deterministic simulation "
        "of context isolation, trusted-state restoration, and "
        "re-execution concepts. It does not claim production "
        "transaction rollback, live-agent memory restoration, "
        "or real infrastructure recovery."
    ),
)