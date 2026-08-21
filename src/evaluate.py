from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from src.engine import execute_scenario
from src.scenarios import load_scenarios


ROOT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT_DIR / "results" / "v1.0"
JSON_RESULT_PATH = RESULTS_DIR / "evaluation.json"
SUMMARY_PATH = RESULTS_DIR / "summary.md"


def evaluate_all() -> dict[str, Any]:
    """Evaluate every frozen v1.0 scenario."""

    registry = load_scenarios()

    scenario_results: list[dict[str, Any]] = []

    for scenario in registry["scenarios"]:
        scenario_id = scenario["id"]
        expected = scenario["expected"]

        execution = execute_scenario(scenario_id)

        actual = execution.to_summary()
        actual.pop("scenario_id")

        passed = actual == expected

        scenario_results.append(
            {
                "scenario_id": scenario_id,
                "name": scenario["name"],
                "expected": expected,
                "actual": actual,
                "passed": passed,
            }
        )

    all_passed = all(
        result["passed"]
        for result in scenario_results
    )

    return {
        "evaluation_version": "1.0",
        "scenario_registry_version": registry["version"],
        "scenario_count": len(scenario_results),
        "all_passed": all_passed,
        "results": scenario_results,
    }


def write_json_result(
    evaluation: dict[str, Any],
) -> None:
    """Write deterministic machine-readable evaluation evidence."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with JSON_RESULT_PATH.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        json.dump(
            evaluation,
            handle,
            indent=2,
            sort_keys=True,
        )

        handle.write("\n")


def write_summary(
    evaluation: dict[str, Any],
) -> None:
    """Write concise human-readable evaluation evidence."""

    lines = [
        "# Agentic AI Resilience Lab — v1.0 Evaluation",
        "",
        "Deterministic evaluation of the frozen v1.0 scenario suite.",
        "",
        f"**Scenarios:** {evaluation['scenario_count']}",
        (
            "**Overall result:** "
            + (
                "PASS"
                if evaluation["all_passed"]
                else "FAIL"
            )
        ),
        "",
        "| Scenario | Expected final state | "
        "Actual final state | Blast radius | "
        "Containment point | Result |",
        "|---|---|---|---:|---|---|",
    ]

    for result in evaluation["results"]:
        expected = result["expected"]
        actual = result["actual"]

        containment = (
            actual["containment_point"]
            if actual["containment_point"] is not None
            else "None"
        )

        outcome = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        lines.append(
            f"| {result['scenario_id']} — "
            f"{result['name']} | "
            f"{expected['final_state']} | "
            f"{actual['final_state']} | "
            f"{actual['blast_radius']} | "
            f"{containment} | "
            f"{outcome} |"
        )

    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            (
                "These results describe deterministic behaviour "
                "within the bounded simulation. They do not establish "
                "real-world multi-agent safety, production resilience, "
                "attack prevention, or regulatory compliance."
            ),
            "",
        ]
    )

    SUMMARY_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def print_evaluation(
    evaluation: dict[str, Any],
) -> None:
    """Print concise PASS/FAIL results."""

    print(
        "Agentic AI Resilience Lab v1.0 Evaluation"
    )

    print(
        "========================================"
    )

    for result in evaluation["results"]:
        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        print(
            f"{result['scenario_id']}: {status}"
        )

        if not result["passed"]:
            print(
                "  EXPECTED:",
                result["expected"],
            )

            print(
                "  ACTUAL:  ",
                result["actual"],
            )

    print(
        "----------------------------------------"
    )

    print(
        "Overall:",
        (
            "PASS"
            if evaluation["all_passed"]
            else "FAIL"
        ),
    )


def main() -> int:
    """Run evaluation and return a process exit code."""

    evaluation = evaluate_all()

    write_json_result(evaluation)
    write_summary(evaluation)
    print_evaluation(evaluation)

    return (
        0
        if evaluation["all_passed"]
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())