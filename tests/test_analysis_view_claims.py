from pathlib import Path


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

CHAOS = (
    ROOT
    / "pages"
    / "4_Chaos_Dashboard.py"
)

MAST = (
    ROOT
    / "pages"
    / "5_MAST_Classifier.py"
)


def test_chaos_does_not_claim_recovery_rate():
    source = CHAOS.read_text(
        encoding="utf-8",
    )

    assert "recovery_rate" not in source
    assert "UI heuristic indicator" in source

    assert (
        "separate from the frozen S01-S08"
        in source
    )


def test_mast_uses_rule_score_not_confidence():
    source = MAST.read_text(
        encoding="utf-8",
    )

    assert "classifier_confidence" not in source
    assert '"rule_score"' in source

    assert (
        "not a trained model"
        in source
    )

    assert (
        "project-local label"
        in source
    )