from pathlib import Path


PAGE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "pages"
    / "6_CASCADE_Isolation.py"
)


def test_isolation_page_uses_canonical_engine():
    source = PAGE.read_text(
        encoding="utf-8",
    )

    assert "execute_scenario" in source
    assert "load_scenarios" in source

    assert (
        "simulate_isolation"
        not in source
    )

    assert (
        "determine_isolation_point"
        not in source
    )


def test_isolation_page_exposes_recovery_trace():
    source = PAGE.read_text(
        encoding="utf-8",
    )

    assert "ROLLBACK_TRIGGERED" in source
    assert "RESTORED" in source
    assert "REEXECUTED" in source