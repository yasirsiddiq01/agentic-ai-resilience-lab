from pathlib import Path


PAGE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "pages"
    / "3_AgentWatch_Tracing.py"
)


def test_agentwatch_uses_canonical_trace():
    source = PAGE.read_text(
        encoding="utf-8",
    )

    assert "execute_scenario" in source
    assert "TraceRecord" in source
    assert "load_scenarios" in source

    assert (
        'elif scenario =='
        not in source
    )

    assert (
        '"Hallucinated root cause":'
        not in source
    )