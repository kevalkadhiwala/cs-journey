import json

import pytest

pytest.importorskip("pydantic")

from app import llm as llm_module  # noqa: E402
from app.incident_report import generate_incident_report  # noqa: E402
from app.llm import LLMError, OllamaProvider, get_llm  # noqa: E402
from app.log_analyzer import LogAnalyzer  # noqa: E402


class FakeLLM:
    """Stands in for a real model: returns prepared answers in order."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.prompts = []

    def complete(self, system, user):
        self.prompts.append(user)
        answer = self.answers.pop(0)

        if isinstance(answer, Exception):
            raise answer
        return answer


GOOD_ANSWER = json.dumps({
    "summary": "192.168.1.99 guessed passwords for admin and keval, "
               "then logged in as admin.",
    "attack_type": "account_compromise",
    "mitre_technique": "T1078",
    "recommended_actions": ["Reset the admin password."],
})


@pytest.fixture
def analyzer(sample_events):
    return LogAnalyzer(sample_events)


def test_ai_report_keeps_facts_from_the_detector(analyzer):
    report = generate_incident_report(analyzer, "192.168.1.99", FakeLLM(GOOD_ANSWER))

    assert report.source == "ai"
    assert report.fallback_reason is None
    assert report.attack_type == "account_compromise"
    assert report.technique_name == "Valid Accounts"
    # Risk and timeline come from the rules, not the model
    assert report.risk_level == "HIGH"
    assert report.timeline[0] == "2026-08-18 09:01:15 LOGIN_FAILED user=admin"
    assert len(report.timeline) == 5


def test_facts_are_sent_to_the_model_as_json(analyzer):
    fake = FakeLLM(GOOD_ANSWER)
    generate_incident_report(analyzer, "192.168.1.99", fake)

    facts = json.loads(fake.prompts[0].removeprefix("Facts:\n"))
    assert facts["ip_address"] == "192.168.1.99"
    assert facts["success_after_failures"] is True


def test_invalid_answer_is_retried_with_the_error(analyzer):
    fake = FakeLLM("this is not json", GOOD_ANSWER)
    report = generate_incident_report(analyzer, "192.168.1.99", fake)

    assert report.source == "ai"
    assert "previous answer was rejected" in fake.prompts[1]


def test_two_bad_answers_fall_back_to_rules(analyzer):
    report = generate_incident_report(
        analyzer, "192.168.1.99", FakeLLM("nope", "{}"))

    assert report.source == "rules"
    assert "failed validation twice" in report.fallback_reason
    assert report.attack_type == "account_compromise"


@pytest.mark.parametrize("bad_change", [
    {"mitre_technique": "T9999"},            # made-up technique
    {"attack_type": "ransomware"},           # not an allowed type
    {"recommended_actions": []},             # no actions
    {"summary": "short"},                    # too short to be useful
])
def test_schema_rejects_bad_fields(analyzer, bad_change):
    bad = json.dumps({**json.loads(GOOD_ANSWER), **bad_change})
    report = generate_incident_report(analyzer, "192.168.1.99", FakeLLM(bad, bad))

    assert report.source == "rules"


def test_unsupported_compromise_claim_is_rejected(analyzer):
    # 192.168.1.77 never logged in successfully
    report = generate_incident_report(
        analyzer, "192.168.1.77", FakeLLM(GOOD_ANSWER, GOOD_ANSWER))

    assert report.source == "rules"
    assert "account_compromise" in report.fallback_reason
    assert report.attack_type == "brute_force"


def test_unreachable_model_falls_back_to_rules(analyzer):
    fake = FakeLLM(LLMError("could not reach the model"))
    report = generate_incident_report(analyzer, "192.168.1.77", fake)

    assert report.source == "rules"
    assert "could not reach" in report.fallback_reason


def test_ai_off_uses_rules(analyzer):
    report = generate_incident_report(analyzer, "192.168.1.77", None)

    assert report.source == "rules"
    assert report.fallback_reason == "AI is switched off"
    assert report.mitre_technique == "T1110.001"


def test_get_llm_reads_the_environment(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    assert get_llm() is None

    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_MODEL", "llama3.2")
    assert isinstance(get_llm(), OllamaProvider)

    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(LLMError):
        get_llm()


def test_ollama_provider_sends_a_json_request(monkeypatch):
    sent = {}

    def fake_post(url, payload, headers=None, timeout=60):
        sent["url"] = url
        sent["payload"] = payload
        return {"message": {"content": "{}"}}

    monkeypatch.setattr(llm_module, "post_json", fake_post)

    assert OllamaProvider().complete("system", "user") == "{}"
    assert sent["url"] == "http://localhost:11434/api/chat"
    assert sent["payload"]["format"] == "json"
