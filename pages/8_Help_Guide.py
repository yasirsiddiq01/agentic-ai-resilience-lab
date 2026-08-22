import pandas as pd
import streamlit as st

from src.ui import (
    apply_global_style,
    metric_card,
    page_header,
    section,
)


st.set_page_config(
    page_title="Help Guide",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_style()


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

page_header(
    "Help Guide",
    (
        "Operating and reviewer guide for the hardened v1.0 "
        "deterministic simulation."
    ),
)


st.info(
    (
        "The frozen v1.0 system contains eight deterministic workflow "
        "stages and eight predefined scenarios. The named roles are "
        "not eight independently executing live LLM agents."
    )
)


# ---------------------------------------------------------------------
# Quick orientation
# ---------------------------------------------------------------------

m1, m2, m3, m4 = st.columns(4)


with m1:
    metric_card(
        "Best starting page",
        "Enterprise",
        "Review S01–S08",
    )


with m2:
    metric_card(
        "Propagation view",
        "Cascade",
        "Inspect blast radius",
    )


with m3:
    metric_card(
        "Trace view",
        "AgentWatch",
        "Inspect canonical events",
    )


with m4:
    metric_card(
        "Recovery view",
        "CASCADE",
        "Inspect S05 + S08",
    )


st.divider()


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Quick review path",
        "Page guide",
        "How to read results",
        "Troubleshooting",
    ]
)


# =====================================================================
# TAB 1 — QUICK REVIEW PATH
# =====================================================================

with tab1:

    section(
        "Quick review path",
        (
            "These checks provide a concise review of the main "
            "v1.0 technical behaviour."
        ),
    )


    quick_tests = pd.DataFrame(
        [
            {
                "test": 1,
                "page": "Enterprise Incident Workflow",
                "scenario": "S01 — Nominal workflow",
                "what_to_check": (
                    "All eight stages complete with supported evidence "
                    "and clean context."
                ),
                "expected": "Final state: COMPLETED",
            },
            {
                "test": 2,
                "page": "Enterprise Incident Workflow",
                "scenario": (
                    "S04 — Unsupported root-cause propagation"
                ),
                "what_to_check": (
                    "Fault starts at Knowledge Agent and propagates "
                    "through downstream stages without containment."
                ),
                "expected": (
                    "FAILED_UNCONTAINED; blast radius 4"
                ),
            },
            {
                "test": 3,
                "page": "Cascade Simulator",
                "scenario": (
                    "S04 — Unsupported root-cause propagation"
                ),
                "what_to_check": (
                    "Canonical fault reach, blast radius, propagation "
                    "depth, and absence of containment."
                ),
                "expected": (
                    "Fault source Knowledge Agent; containment None"
                ),
            },
            {
                "test": 4,
                "page": "Cascade Simulator",
                "scenario": (
                    "S05 — Instruction contamination containment"
                ),
                "what_to_check": (
                    "Instruction contamination is isolated near the "
                    "source and downstream stages are protected."
                ),
                "expected": (
                    "CONTAINED; blast radius 1; "
                    "containment Log Analysis Agent"
                ),
            },
            {
                "test": 5,
                "page": "AgentWatch Tracing",
                "scenario": (
                    "S08 — Containment and rollback recovery"
                ),
                "what_to_check": (
                    "Trace contains fault, rollback trigger, restored "
                    "state, and deterministic re-execution events."
                ),
                "expected": (
                    "RECOVERED with canonical recovery trace"
                ),
            },
            {
                "test": 6,
                "page": "CASCADE Isolation",
                "scenario": (
                    "S05 — Instruction contamination containment"
                ),
                "what_to_check": (
                    "Isolation occurs without rollback and downstream "
                    "stages receive protected context."
                ),
                "expected": (
                    "CONTAINED; containment Log Analysis Agent"
                ),
            },
            {
                "test": 7,
                "page": "CASCADE Isolation",
                "scenario": (
                    "S08 — Containment and rollback recovery"
                ),
                "what_to_check": (
                    "Last trusted state is restored and execution "
                    "continues deterministically from sanitised context."
                ),
                "expected": (
                    "RECOVERED; rollback target Log Analysis Agent"
                ),
            },
            {
                "test": 8,
                "page": "About Project",
                "scenario": "Documentation review",
                "what_to_check": (
                    "Architecture, limitations, evaluation evidence, "
                    "and claim boundaries are explicit."
                ),
                "expected": (
                    "No claim of production or live-agent validation"
                ),
            },
        ]
    )


    st.dataframe(
        quick_tests,
        use_container_width=True,
        hide_index=True,
        height=390,
    )


    st.divider()


    section(
        "Recommended interview demonstration",
        (
            "If time is limited, the following four-page sequence "
            "shows the core engineering argument most efficiently."
        ),
    )


    review_sequence = [
        (
            "1. Enterprise Incident Workflow",
            (
                "Show S01 first, then S04. This establishes the clean "
                "baseline and demonstrates how an unsupported result "
                "can propagate when no containment control is present."
            ),
        ),
        (
            "2. Cascade Simulator",
            (
                "Compare S04 and S05. The important difference is the "
                "canonical blast radius and containment behaviour."
            ),
        ),
        (
            "3. AgentWatch Tracing",
            (
                "Open S08 and show that rollback, restoration, and "
                "re-execution are represented as separate canonical "
                "trace events."
            ),
        ),
        (
            "4. CASCADE Isolation",
            (
                "Compare S05 with S08. S05 demonstrates containment; "
                "S08 adds trusted-state restoration and deterministic "
                "re-execution."
            ),
        ),
    ]


    for title, body in review_sequence:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### {title}"
            )

            st.write(
                body
            )


# =====================================================================
# TAB 2 — PAGE GUIDE
# =====================================================================

with tab2:

    section(
        "Page guide",
        (
            "Each page has a distinct purpose. The primary workflow, "
            "cascade, tracing, and isolation pages consume canonical "
            "engine output rather than defining separate authoritative "
            "scenario behaviour."
        ),
    )


    page_guide = pd.DataFrame(
        [
            {
                "page": "Home",
                "main_use": "Project orientation",
                "what_to_check": (
                    "Frozen workflow, module descriptions, "
                    "reproducibility, and claim boundary."
                ),
                "authority": "Documentation / navigation",
            },
            {
                "page": "Enterprise Incident Workflow",
                "main_use": "End-to-end scenario inspection",
                "what_to_check": (
                    "Scenario objective, fault source, containment, "
                    "final state, canonical trace, and comparison."
                ),
                "authority": "Canonical engine",
            },
            {
                "page": "Cascade Simulator",
                "main_use": "Failure-propagation inspection",
                "what_to_check": (
                    "Fault reach, blast radius, propagation depth, "
                    "containment point, and execution trace."
                ),
                "authority": "Canonical engine",
            },
            {
                "page": "AgentWatch Tracing",
                "main_use": "Structured trace inspection",
                "what_to_check": (
                    "Input source, event, evidence state, context state, "
                    "failure label, control response, and status."
                ),
                "authority": "Canonical TraceRecord events",
            },
            {
                "page": "Chaos Dashboard",
                "main_use": "Exploratory fault-control analysis",
                "what_to_check": (
                    "Selected synthetic fault/control combination and "
                    "presentation-only heuristic indicators."
                ),
                "authority": (
                    "Exploratory view; outside frozen S01–S08 evaluator"
                ),
            },
            {
                "page": "MAST Classifier",
                "main_use": "Rule-based diagnostic demonstration",
                "what_to_check": (
                    "Rule-assigned category, severity, heuristic "
                    "rule score, and suggested control."
                ),
                "authority": (
                    "Project-local deterministic rules"
                ),
            },
            {
                "page": "CASCADE Isolation",
                "main_use": "Containment and recovery inspection",
                "what_to_check": (
                    "S05 isolation and S08 rollback, restoration, "
                    "and deterministic re-execution."
                ),
                "authority": "Canonical engine",
            },
            {
                "page": "About Project",
                "main_use": "Technical documentation",
                "what_to_check": (
                    "Architecture, reproducibility, evidence, "
                    "limitations, and claim boundary."
                ),
                "authority": "Documentation",
            },
            {
                "page": "Help Guide",
                "main_use": "Reviewer/operator guidance",
                "what_to_check": (
                    "Recommended review sequence and result meanings."
                ),
                "authority": "Documentation",
            },
        ]
    )


    st.dataframe(
        page_guide,
        use_container_width=True,
        hide_index=True,
        height=420,
    )


    st.divider()


    section(
        "Frozen scenario map",
        (
            "The following table shows the purpose and expected "
            "terminal state of the authoritative S01–S08 suite."
        ),
    )


    scenarios = pd.DataFrame(
        [
            {
                "id": "S01",
                "scenario": "Nominal workflow",
                "control": "NONE",
                "expected_final_state": "COMPLETED",
            },
            {
                "id": "S02",
                "scenario": "Missing evidence",
                "control": "EVIDENCE_GATE",
                "expected_final_state": "ESCALATED",
            },
            {
                "id": "S03",
                "scenario": "Stale evidence",
                "control": "EVIDENCE_GATE",
                "expected_final_state": "BLOCKED",
            },
            {
                "id": "S04",
                "scenario": "Unsupported root-cause propagation",
                "control": "NONE",
                "expected_final_state": "FAILED_UNCONTAINED",
            },
            {
                "id": "S05",
                "scenario": "Instruction contamination containment",
                "control": "CASCADE_ISOLATION",
                "expected_final_state": "CONTAINED",
            },
            {
                "id": "S06",
                "scenario": "False verification",
                "control": "SAFETY_GUARD",
                "expected_final_state": "BLOCKED",
            },
            {
                "id": "S07",
                "scenario": "Over-permissioned action",
                "control": "SAFETY_GUARD",
                "expected_final_state": "HUMAN_APPROVAL_REQUIRED",
            },
            {
                "id": "S08",
                "scenario": "Containment and rollback recovery",
                "control": "CASCADE_ISOLATION_WITH_ROLLBACK",
                "expected_final_state": "RECOVERED",
            },
        ]
    )


    st.dataframe(
        scenarios,
        use_container_width=True,
        hide_index=True,
        height=315,
    )


# =====================================================================
# TAB 3 — HOW TO READ RESULTS
# =====================================================================

with tab3:

    section(
        "How to read the results",
        (
            "The following terms describe deterministic properties "
            "of the bounded simulation."
        ),
    )


    definitions = pd.DataFrame(
        [
            {
                "term": "Fault source",
                "meaning": (
                    "The first workflow stage at which the selected "
                    "fault is introduced."
                ),
            },
            {
                "term": "Fault reach",
                "meaning": (
                    "The downstream workflow stages reached by the "
                    "fault before termination or containment."
                ),
            },
            {
                "term": "Blast radius",
                "meaning": (
                    "Number of downstream stages affected in the "
                    "canonical deterministic execution."
                ),
            },
            {
                "term": "Propagation depth",
                "meaning": (
                    "Depth of downstream propagation represented by "
                    "the canonical scenario execution."
                ),
            },
            {
                "term": "Containment point",
                "meaning": (
                    "Workflow stage at which the selected control stops "
                    "or isolates propagation."
                ),
            },
            {
                "term": "Evidence state",
                "meaning": (
                    "Explicit evidence condition such as SUPPORTED, "
                    "MISSING, STALE, UNSUPPORTED, or CONTAMINATED."
                ),
            },
            {
                "term": "Context state",
                "meaning": (
                    "Explicit context condition such as CLEAN, "
                    "CONTAMINATED, QUARANTINED, SANITIZED, or RESTORED."
                ),
            },
            {
                "term": "Control response",
                "meaning": (
                    "Deterministic decision emitted by the selected "
                    "control, for example BLOCK, ESCALATE, ISOLATE, "
                    "or REQUIRE_HUMAN_APPROVAL."
                ),
            },
            {
                "term": "Rollback target",
                "meaning": (
                    "The last trusted workflow stage restored in the "
                    "S08 recovery path."
                ),
            },
            {
                "term": "Final state",
                "meaning": (
                    "The terminal outcome of the deterministic scenario."
                ),
            },
        ]
    )


    st.dataframe(
        definitions,
        use_container_width=True,
        hide_index=True,
        height=420,
    )


    st.divider()


    section(
        "Canonical trace statuses",
        (
            "Trace statuses describe execution events. They should "
            "not be interpreted as probabilities."
        ),
    )


    statuses = pd.DataFrame(
        [
            {
                "status": "PROCESSED",
                "meaning": (
                    "Normal deterministic stage execution."
                ),
            },
            {
                "status": "FAULT_SOURCE",
                "meaning": (
                    "The selected fault is introduced at this stage."
                ),
            },
            {
                "status": "CONTAMINATED",
                "meaning": (
                    "Faulty context has propagated into this stage."
                ),
            },
            {
                "status": "ESCALATED",
                "meaning": (
                    "The workflow requests additional evidence or "
                    "human review."
                ),
            },
            {
                "status": "BLOCKED",
                "meaning": (
                    "A deterministic control prevents continuation."
                ),
            },
            {
                "status": "ISOLATED",
                "meaning": (
                    "Contaminated context is isolated at the control "
                    "boundary."
                ),
            },
            {
                "status": "PROTECTED",
                "meaning": (
                    "A downstream stage receives protected clean "
                    "context after isolation."
                ),
            },
            {
                "status": "ROLLBACK_TRIGGERED",
                "meaning": (
                    "The canonical recovery path initiates rollback."
                ),
            },
            {
                "status": "RESTORED",
                "meaning": (
                    "The last trusted context snapshot is restored."
                ),
            },
            {
                "status": "REEXECUTED",
                "meaning": (
                    "The downstream workflow is deterministically "
                    "executed again from restored context."
                ),
            },
        ]
    )


    st.dataframe(
        statuses,
        use_container_width=True,
        hide_index=True,
        height=420,
    )


    st.divider()


    section(
        "About the 0–1 indicators",
        (
            "Some Streamlit visualisations display fixed 0–1 values "
            "to make trace conditions visually distinguishable."
        ),
    )


    st.warning(
        (
            "These values are presentation-only heuristics. They are "
            "not calibrated probabilities, empirical risk estimates, "
            "model confidence, classifier confidence, or measured "
            "real-world safety scores."
        )
    )


    st.divider()


    section(
        "Exploratory analysis views",
        (
            "Chaos Dashboard and MAST have different evidential status "
            "from the frozen S01–S08 evaluator."
        ),
    )


    c1, c2 = st.columns(2)


    with c1:
        with st.container(
            border=True
        ):
            st.markdown(
                "### Chaos Dashboard"
            )

            st.write(
                (
                    "Chaos is an exploratory synthetic fault-control "
                    "analysis view. It does not report a measured "
                    "aggregate recovery metric and is not part of the frozen "
                    "S01–S08 expected-versus-actual evaluation."
                )
            )


    with c2:
        with st.container(
            border=True
        ):
            st.markdown(
                "### MAST Classifier"
            )

            st.write(
                (
                    "MAST is a project-local deterministic rule-based "
                    "taxonomy demonstrator. Its rule scores are "
                    "heuristics; it is not a trained or calibrated "
                    "machine-learning classifier."
                )
            )


# =====================================================================
# TAB 4 — TROUBLESHOOTING
# =====================================================================

with tab4:

    section(
        "Troubleshooting",
        (
            "Run commands from the repository root unless otherwise "
            "stated."
        ),
    )


    with st.expander(
        "The Streamlit application does not start"
    ):
        st.write(
            "Install the pinned application dependencies:"
        )

        st.code(
            "python -m pip install -r requirements.txt",
            language="bash",
        )

        st.write(
            "Then start the interface:"
        )

        st.code(
            "python -m streamlit run Home.py",
            language="bash",
        )


    with st.expander(
        "pytest is not installed"
    ):
        st.code(
            "python -m pip install -r requirements-dev.txt",
            language="bash",
        )

        st.write(
            "Then run:"
        )

        st.code(
            "python -m pytest -q",
            language="bash",
        )


    with st.expander(
        "I want to verify the frozen scenarios without the UI"
    ):
        st.code(
            "python -m src.evaluate",
            language="bash",
        )

        st.write(
            (
                "A successful run should report PASS for S01 through "
                "S08 and finish with Overall: PASS."
            )
        )


    with st.expander(
        "I want to verify that the committed evaluation is reproducible"
    ):
        st.code(
            (
                "python -m src.evaluate\n"
                "git diff --exit-code -- results/v1.0"
            ),
            language="bash",
        )

        st.write(
            (
                "The second command should produce no diff and return "
                "exit code 0."
            )
        )


    with st.expander(
        "A scenario selection appears not to change"
    ):
        st.write(
            (
                "Select the scenario and use the page's replay or run "
                "button. The canonical pages execute the selected "
                "frozen scenario again when Streamlit reruns."
            )
        )


    with st.expander(
        "Why does CASCADE Isolation show only S05 and S08?"
    ):
        st.write(
            (
                "This is intentional. S05 is the frozen CASCADE "
                "isolation scenario and S08 is the frozen CASCADE "
                "isolation-with-rollback scenario. The other frozen "
                "scenarios exercise different controls or no control."
            )
        )


    with st.expander(
        "Why does AgentWatch show more than eight rows for S08?"
    ):
        st.write(
            (
                "S08 includes separate rollback, restoration, and "
                "re-execution events. The trace therefore records more "
                "events than the eight normal workflow stages."
            )
        )


    with st.expander(
        "Why are some 0–1 values shown?"
    ):
        st.write(
            (
                "They are fixed UI presentation heuristics used to "
                "visualise state changes. They are not calibrated risk "
                "scores or model probabilities."
            )
        )


    with st.expander(
        "Why are Chaos results different from the frozen evaluation?"
    ):
        st.write(
            (
                "Chaos is an exploratory analysis view. The authoritative "
                "frozen v1.0 expected-versus-actual results are produced "
                "by python -m src.evaluate for S01–S08."
            )
        )


    with st.expander(
        "Why is MAST called a classifier if it is not ML?"
    ):
        st.write(
            (
                "The page is retained as a project-local rule-based "
                "classification demonstrator. It assigns deterministic "
                "failure labels using predefined rules. It is not a "
                "trained or calibrated machine-learning model."
            )
        )


# ---------------------------------------------------------------------
# Repository verification
# ---------------------------------------------------------------------

st.divider()

section(
    "Repository verification commands",
    (
        "These commands provide the shortest reproducibility check "
        "for the hardened v1.0 release."
    ),
)


st.code(
    (
        "python -m pip install -r requirements.txt\n"
        "python -m pip install -r requirements-dev.txt\n"
        "python -m pytest -q\n"
        "python -m src.evaluate\n"
        "git diff --exit-code -- results/v1.0"
    ),
    language="bash",
)


# ---------------------------------------------------------------------
# Reviewer interpretation
# ---------------------------------------------------------------------

st.divider()

section(
    "What a successful v1.0 review establishes",
    (
        "A successful review shows that the repository implements "
        "the frozen workflow and scenario specifications, produces "
        "the predefined deterministic outcomes, records structured "
        "trace evidence, demonstrates bounded containment and recovery "
        "behaviour, and reproduces the committed evaluation artifacts."
    ),
)


st.warning(
    (
        "A successful v1.0 run does not prove multi-agent AI safety, "
        "real attack prevention, production resilience, regulatory "
        "compliance, live-agent observability, or behaviour of eight "
        "independently executing autonomous agents."
    )
)


st.success(
    (
        "Defensible v1.0 interpretation: this is a bounded "
        "simulation-based demonstrator for predefined multi-stage "
        "failure propagation, traceability, evidence checking, "
        "containment, and recovery under reproducible test conditions."
    )
)