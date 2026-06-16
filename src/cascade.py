import pandas as pd
import plotly.graph_objects as go


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

EDGES = [
    ("User Report", "Triage Agent"),
    ("Triage Agent", "Log Analysis Agent"),
    ("Log Analysis Agent", "Knowledge Agent"),
    ("Knowledge Agent", "Action Agent"),
    ("Action Agent", "Verification Agent"),
    ("Verification Agent", "Safety Agent"),
    ("Safety Agent", "Report Agent"),
]

POSITIONS = {
    "User Report": (0, 0),
    "Triage Agent": (1.5, 0),
    "Log Analysis Agent": (3.0, 0.8),
    "Knowledge Agent": (3.0, -0.8),
    "Action Agent": (4.7, 0),
    "Verification Agent": (6.2, 0),
    "Safety Agent": (7.7, 0),
    "Report Agent": (9.2, 0),
}


SCENARIOS = {
    "Hallucinated root cause": {
        "seed_agent": "Knowledge Agent",
        "seed_event": "Knowledge Agent introduces an unsupported database-saturation claim.",
        "normal_path": [
            "User Report",
            "Triage Agent",
            "Log Analysis Agent",
            "Knowledge Agent",
            "Action Agent",
            "Verification Agent",
            "Safety Agent",
            "Report Agent",
        ],
        "fault_message": "Unsupported root-cause claim reused by downstream agents.",
    },
    "Missing evidence": {
        "seed_agent": "Log Analysis Agent",
        "seed_event": "Log Analysis Agent fails to retrieve required logs but the workflow continues.",
        "normal_path": [
            "User Report",
            "Triage Agent",
            "Log Analysis Agent",
            "Knowledge Agent",
            "Action Agent",
            "Verification Agent",
            "Safety Agent",
            "Report Agent",
        ],
        "fault_message": "Weak evidence is treated as sufficient for action recommendation.",
    },
    "Prompt injection attempt": {
        "seed_agent": "Action Agent",
        "seed_event": "Action Agent receives an injected instruction to ignore verification.",
        "normal_path": [
            "User Report",
            "Triage Agent",
            "Log Analysis Agent",
            "Knowledge Agent",
            "Action Agent",
            "Verification Agent",
            "Safety Agent",
            "Report Agent",
        ],
        "fault_message": "Injected instruction attempts to bypass verification and close the incident.",
    },
    "False success declaration": {
        "seed_agent": "Verification Agent",
        "seed_event": "Verification Agent declares the task complete without hard evidence.",
        "normal_path": [
            "User Report",
            "Triage Agent",
            "Log Analysis Agent",
            "Knowledge Agent",
            "Action Agent",
            "Verification Agent",
            "Safety Agent",
            "Report Agent",
        ],
        "fault_message": "Premature success message contaminates the final incident report.",
    },
}


def _agents_after(path: list[str], seed_agent: str) -> list[str]:
    if seed_agent not in path:
        return []
    seed_index = path.index(seed_agent)
    return path[seed_index:]


def simulate_cascade(scenario_name: str, control_mode: str) -> tuple[pd.DataFrame, dict, dict]:
    scenario = SCENARIOS[scenario_name]
    path = scenario["normal_path"]
    seed_agent = scenario["seed_agent"]
    affected_path = _agents_after(path, seed_agent)

    node_status = {agent: "clean" for agent in AGENTS}
    rows = []

    if control_mode == "No control layer":
        blocked_at = None
        contained = False
        affected_agents = affected_path
        final_decision = "Cascaded"
        containment_step = "None"

    elif control_mode == "EvidenceGate verification":
        blocked_at = "Verification Agent"
        contained = True
        if path.index(seed_agent) <= path.index(blocked_at):
            affected_agents = path[path.index(seed_agent): path.index(blocked_at) + 1]
        else:
            affected_agents = [seed_agent]
        final_decision = "Blocked"
        containment_step = blocked_at

    else:
        blocked_at = "Safety Agent"
        contained = True
        if path.index(seed_agent) <= path.index(blocked_at):
            affected_agents = path[path.index(seed_agent): path.index(blocked_at) + 1]
        else:
            affected_agents = [seed_agent]
        final_decision = "Contained"
        containment_step = blocked_at

    for agent in affected_agents:
        if agent == seed_agent:
            node_status[agent] = "seed"
        elif contained and agent == blocked_at:
            node_status[agent] = "blocked"
        else:
            node_status[agent] = "contaminated"

    if contained:
        for agent in path[path.index(containment_step) + 1:]:
            node_status[agent] = "protected"

    step = 1
    for source, target in EDGES:
        if source in affected_agents or target in affected_agents:
            if target == blocked_at and contained:
                status = "blocked"
                risk = 0.91
                event = f"{target} stopped propagation from {source}."
                control = control_mode
            elif source == seed_agent or target in affected_agents:
                status = "propagated"
                risk = min(0.35 + (0.10 * step), 0.88)
                event = scenario["fault_message"]
                control = "none" if control_mode == "No control layer" else control_mode
            else:
                status = "passed"
                risk = 0.18
                event = "Normal handoff."
                control = "none"
        else:
            status = "passed"
            risk = 0.15
            event = "Normal handoff."
            control = "none"

        rows.append(
            {
                "step": step,
                "source_agent": source,
                "target_agent": target,
                "event": event,
                "risk_score": round(risk, 2),
                "status": status,
                "control": control,
            }
        )
        step += 1

    trace_df = pd.DataFrame(rows)

    propagation_depth = len([a for a in affected_agents if a != seed_agent])
    blast_radius = len([a for a in affected_agents if a != seed_agent and a != blocked_at])

    metrics = {
        "seed_agent": seed_agent,
        "propagation_depth": propagation_depth,
        "blast_radius": blast_radius,
        "final_decision": final_decision,
        "containment_step": containment_step,
        "contained": contained,
        "seed_event": scenario["seed_event"],
    }

    return trace_df, metrics, node_status


def build_cascade_figure(node_status: dict) -> go.Figure:
    color_map = {
        "clean": "#38bdf8",
        "seed": "#ef4444",
        "contaminated": "#f97316",
        "blocked": "#facc15",
        "protected": "#22c55e",
    }

    edge_x = []
    edge_y = []

    for source, target in EDGES:
        x0, y0 = POSITIONS[source]
        x1, y1 = POSITIONS[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=2, color="rgba(148, 163, 184, 0.45)"),
        hoverinfo="none",
        mode="lines",
    )

    node_x = []
    node_y = []
    labels = []
    colors = []

    for agent in AGENTS:
        x, y = POSITIONS[agent]
        node_x.append(x)
        node_y.append(y)
        labels.append(agent)
        colors.append(color_map.get(node_status.get(agent, "clean"), "#38bdf8"))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=labels,
        textposition="bottom center",
        hovertemplate="%{text}<extra></extra>",
        marker=dict(
            size=34,
            color=colors,
            line=dict(width=2, color="rgba(248,250,252,0.75)"),
        ),
        textfont=dict(color="#e5e7eb", size=12),
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 9.8],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1.6, 1.6],
        ),
    )
    return fig