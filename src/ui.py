import streamlit as st


def apply_global_style():
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-family: "Segoe UI", sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #07111f 0%, #0b1728 45%, #101827 100%);
        }

        .stApp {
            color: #f8fafc;
        }

        /* Remove white top header feel */
        [data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0);
            height: 0rem;
        }

        /* Remove top decoration line */
        [data-testid="stDecoration"] {
            display: none;
        }

        /* Main content container */
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1450px;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #06101d 0%, #091426 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.16);
            min-width: 250px !important;
            max-width: 250px !important;
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.3rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        [data-testid="stSidebarNav"] {
            background: transparent;
        }

        [data-testid="stSidebarNav"]::before {
            content: "Navigation";
            display: block;
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }

        [data-testid="stSidebarNav"] a {
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.10);
            border-radius: 12px;
            margin-bottom: 0.35rem;
            padding: 0.45rem 0.55rem;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.25);
        }

        [data-testid="stSidebarNav"] span {
            color: #e2e8f0 !important;
            font-size: 0.92rem;
        }

        /* Main hero area */
        .hero-card {
            padding: 1.8rem 1.8rem 1.5rem 1.8rem;
            border-radius: 24px;
            border: 1px solid rgba(56, 189, 248, 0.24);
            background: linear-gradient(145deg, rgba(8, 15, 30, 0.96), rgba(17, 24, 39, 0.92));
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.30);
            margin-bottom: 1.4rem;
        }

        .main-title {
            font-size: 2.6rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #f8fafc;
            margin-bottom: 0.55rem;
            line-height: 1.15;
        }

        .subtitle {
            font-size: 1.06rem;
            color: #cbd5e1;
            max-width: 980px;
            line-height: 1.7;
            margin-bottom: 0;
        }

        /* Stronger main working area feel */
        .content-panel {
            padding: 1rem;
            border-radius: 20px;
            background: rgba(9, 16, 30, 0.35);
            border: 1px solid rgba(148, 163, 184, 0.10);
            margin-bottom: 1rem;
        }

        .metric-card {
            padding: 1rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.18);
            min-height: 110px;
        }

        .metric-label {
            color: #94a3b8;
            font-size: 0.85rem;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            color: #f8fafc;
            font-size: 1.65rem;
            font-weight: 800;
        }

        .metric-note {
            color: #cbd5e1;
            font-size: 0.82rem;
            margin-top: 0.35rem;
            line-height: 1.45;
        }

        .module-card {
            padding: 1.2rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.18);
            min-height: 190px;
            margin-bottom: 1rem;
        }

        .module-card h3 {
            color: #f8fafc;
            margin-bottom: 0.35rem;
            font-size: 1.1rem;
        }

        .module-card p {
            color: #cbd5e1;
            line-height: 1.55;
            font-size: 0.95rem;
        }

        .tag {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: rgba(14, 165, 233, 0.14);
            color: #7dd3fc;
            border: 1px solid rgba(125, 211, 252, 0.22);
            font-size: 0.75rem;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        .warning-tag {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(251, 191, 36, 0.25);
            font-size: 0.75rem;
        }

        .danger-tag {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: rgba(239, 68, 68, 0.15);
            color: #fca5a5;
            border: 1px solid rgba(252, 165, 165, 0.25);
            font-size: 0.75rem;
        }

        .success-tag {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.14);
            color: #86efac;
            border: 1px solid rgba(134, 239, 172, 0.22);
            font-size: 0.75rem;
        }

        .agent-card {
            padding: 1rem;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.2);
            margin-bottom: 0.8rem;
            min-height: 145px;
        }

        .agent-name {
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .agent-desc {
            color: #cbd5e1;
            font-size: 0.88rem;
            line-height: 1.45;
        }

        .section-heading {
            color: #f8fafc;
            font-size: 1.45rem;
            font-weight: 800;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        .section-copy {
            color: #cbd5e1;
            font-size: 0.96rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 16px;
            overflow: hidden;
        }

        div[data-testid="stAlert"] {
            border-radius: 14px;
        }
	        .stButton > button {
            background: linear-gradient(135deg, #0284c7, #0369a1) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(125, 211, 252, 0.35) !important;
            border-radius: 14px !important;
            padding: 0.65rem 1rem !important;
            font-weight: 700 !important;
            box-shadow: 0 10px 24px rgba(2, 132, 199, 0.22);
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
            border: 1px solid rgba(186, 230, 253, 0.65) !important;
            color: #ffffff !important;
        }

        .stButton > button:disabled {
            background: rgba(148, 163, 184, 0.18) !important;
            color: rgba(226, 232, 240, 0.45) !important;
            border: 1px solid rgba(148, 163, 184, 0.14) !important;
            box-shadow: none !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #f8fafc !important;
            border-radius: 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="main-title">{title}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def module_card(title: str, body: str, tags: list[str]):
    tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in tags])
    st.markdown(
        f"""
        <div class="module-card">
            <h3>{title}</h3>
            <p>{body}</p>
            <div>{tags_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, copy: str = ""):
    st.markdown(f'<div class="section-heading">{title}</div>', unsafe_allow_html=True)
    if copy:
        st.markdown(f'<div class="section-copy">{copy}</div>', unsafe_allow_html=True)


def status_tag(status: str):
    status_lower = status.lower()
    if status_lower in ["blocked", "high risk", "failed", "unsafe"]:
        css_class = "danger-tag"
    elif status_lower in ["warning", "elevated", "needs review", "escalated"]:
        css_class = "warning-tag"
    elif status_lower in ["verified", "contained", "safe", "passed", "approved"]:
        css_class = "success-tag"
    else:
        css_class = "tag"

    return f'<span class="{css_class}">{status}</span>'


def agent_card(name: str, role: str, status: str):
    st.markdown(
        f"""
        <div class="agent-card">
            <div class="agent-name">{name}</div>
            <div>{status_tag(status)}</div>
            <div class="agent-desc" style="margin-top:0.7rem;">{role}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_agent_flow_animation(
    title="Animated agent workflow",
    subtitle="Live movement across the multi-agent workflow",
    stop_agent="Report Agent",
    fault_agent=None,
    isolated_agent=None,
    height=390,
):
    import html
    import streamlit.components.v1 as components

    agents = [
        "User Report",
        "Triage Agent",
        "Log Analysis Agent",
        "Knowledge Agent",
        "Action Agent",
        "Verification Agent",
        "Safety Agent",
        "Report Agent",
    ]

    positions = {
        "User Report": (80, 160),
        "Triage Agent": (185, 160),
        "Log Analysis Agent": (305, 90),
        "Knowledge Agent": (305, 230),
        "Action Agent": (435, 160),
        "Verification Agent": (565, 160),
        "Safety Agent": (695, 160),
        "Report Agent": (825, 160),
    }

    edges = [
        ("User Report", "Triage Agent"),
        ("Triage Agent", "Log Analysis Agent"),
        ("Log Analysis Agent", "Knowledge Agent"),
        ("Knowledge Agent", "Action Agent"),
        ("Action Agent", "Verification Agent"),
        ("Verification Agent", "Safety Agent"),
        ("Safety Agent", "Report Agent"),
    ]

    if stop_agent not in agents:
        stop_agent = "Report Agent"

    stop_index = agents.index(stop_agent)
    path_agents = agents[: stop_index + 1]

    path_commands = []

    for index, agent in enumerate(path_agents):
        x, y = positions[agent]
        if index == 0:
            path_commands.append(f"M {x} {y}")
        else:
            path_commands.append(f"L {x} {y}")

    motion_path = " ".join(path_commands)
    duration = max(2.8, len(path_agents) * 0.55)

    edge_lines = []

    for source, target in edges:
        x1, y1 = positions[source]
        x2, y2 = positions[target]

        edge_lines.append(
            f"""
            <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
                  stroke="rgba(148,163,184,0.38)"
                  stroke-width="3" />
            """
        )

    node_items = []

    for index, agent in enumerate(agents):
        x, y = positions[agent]

        if agent == fault_agent:
            final_color = "#ef4444"
            label = "fault seed"
        elif agent == isolated_agent:
            final_color = "#facc15"
            label = "isolation"
        elif index <= stop_index:
            final_color = "#38bdf8"
            label = "active"
        else:
            final_color = "#475569"
            label = "pending"

        begin_time = index * 0.55 if index <= stop_index else duration + 1

        safe_agent = html.escape(agent)
        safe_label = html.escape(label)

        node_items.append(
            f"""
            <g>
                <circle cx="{x}" cy="{y}" r="18"
                        fill="#475569"
                        stroke="rgba(248,250,252,0.85)"
                        stroke-width="3">
                    <animate attributeName="fill"
                             from="#475569"
                             to="{final_color}"
                             begin="{begin_time}s"
                             dur="0.25s"
                             fill="freeze" />
                </circle>

                <circle cx="{x}" cy="{y}" r="24"
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
                             values="20;31;24"
                             begin="{begin_time}s"
                             dur="0.65s"
                             fill="freeze" />
                </circle>

                <text x="{x}" y="{y + 42}"
                      text-anchor="middle"
                      fill="#e5e7eb"
                      font-size="13"
                      font-weight="600">{safe_agent}</text>

                <text x="{x}" y="{y + 58}"
                      text-anchor="middle"
                      fill="#94a3b8"
                      font-size="11">{safe_label}</text>
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
                background: rgba(15, 23, 42, 0.58);
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
                filter: drop-shadow(0 0 8px rgba(56,189,248,0.9));
            }}
        </style>
    </head>

    <body>
        <div class="graph-card">
            <div class="title-row">
                <div class="title">{html.escape(title)}</div>
                <div class="status">{html.escape(subtitle)}</div>
            </div>

            <svg viewBox="0 0 900 315" width="100%" height="355">
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

                <circle r="10"
                        fill="#ffffff"
                        stroke="#38bdf8"
                        stroke-width="5"
                        class="runner">
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

    components.html(html_code, height=height, scrolling=False)