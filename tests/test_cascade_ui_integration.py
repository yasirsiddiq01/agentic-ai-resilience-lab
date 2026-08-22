from pathlib import Path


PAGE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "pages"
    / "2_Cascade_Simulator.py"
)


def test_cascade_page_uses_canonical_engine():
    source = PAGE.read_text(
        encoding="utf-8",
    )

    assert "execute_scenario" in source
    assert "get_trace_rows" in source
    assert "simulate_cascade" not in source