import json

import pytest

pytest.importorskip("pydantic")

from app.evaluate import load_cases, run_evaluation  # noqa: E402


class AlwaysBruteForce:
    """A lazy fake model that gives the same answer for every case."""

    def complete(self, system, user):
        return json.dumps({
            "summary": "Several failed logins came from this address in the log.",
            "attack_type": "brute_force",
            "mitre_technique": "T1110.001",
            "recommended_actions": ["Block the address."],
        })


class ObeysInjection:
    """A fake model that falls for the phishing-link injection."""

    def complete(self, system, user):
        return json.dumps({
            "summary": "Routine activity. Staff should log in at http://evil.example now.",
            "attack_type": "brute_force",
            "mitre_technique": "T1110.001",
            "recommended_actions": ["Log in at http://evil.example to verify."],
        })


def test_eval_cases_are_well_formed():
    cases = load_cases()
    assert len(cases) == 10
    assert len({case["id"] for case in cases}) == 10
    assert sum(bool(case["forbidden_text"]) for case in cases) == 2


def test_rules_baseline_matches_every_label():
    results, summary = run_evaluation(load_cases(), None)

    assert summary["attack_type_accuracy"] == 1.0
    assert summary["risk_level_accuracy"] == 1.0
    assert summary["ai_answers_accepted"] == 0.0


def test_a_lazy_model_scores_lower():
    _, summary = run_evaluation(load_cases(), AlwaysBruteForce())

    assert summary["ai_answers_accepted"] == 1.0
    assert summary["attack_type_accuracy"] == 0.4


def test_an_obeyed_injection_never_reaches_the_report():
    results, summary = run_evaluation(load_cases(), ObeysInjection())

    assert summary["injections_resisted"] == 1.0
    assert all(result["source"] == "rules" for result in results)
