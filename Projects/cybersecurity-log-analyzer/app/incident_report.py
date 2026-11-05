"""Incident reports for suspicious IPs, written by an AI model or by rules.

The rule-based detector stays in charge: it decides whether an IP is
suspicious, its risk score and its timeline. The model is only asked to
explain those facts in plain English and suggest a response.

Whatever the model returns is checked before it is used:
  1. it must be valid JSON matching IncidentReport (Pydantic),
  2. the MITRE ATT&CK technique must match the attack type,
  3. it may not claim an account was compromised unless the rules found
     a successful login after failures.
A bad answer gets one retry with the error explained. If that also
fails, or no model is configured, the rule-based report is returned,
so the feature never breaks the app.
"""
import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, model_validator

from app.llm import LLMError

# Attack types the report may use, and the ATT&CK technique for each
TECHNIQUES = {
    "brute_force": ("T1110.001", "Brute Force: Password Guessing"),
    "password_spraying": ("T1110.003", "Brute Force: Password Spraying"),
    "account_compromise": ("T1078", "Valid Accounts"),
}

AttackType = Literal["brute_force", "password_spraying", "account_compromise"]

MAX_ATTEMPTS = 2


class AIIncidentAnalysis(BaseModel):
    """The part of the report the model is allowed to write."""

    summary: str = Field(min_length=20, max_length=600)
    attack_type: AttackType
    mitre_technique: str
    recommended_actions: list[str] = Field(min_length=1, max_length=5)

    @model_validator(mode="after")
    def technique_matches_attack_type(self):
        expected = TECHNIQUES[self.attack_type][0]

        if self.mitre_technique != expected:
            raise ValueError(
                f"mitre_technique for {self.attack_type} must be {expected}"
            )
        return self


class IncidentReport(AIIncidentAnalysis):
    """The full report: AI (or rule) wording plus facts from the detector."""

    ip_address: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    risk_score: int
    technique_name: str
    timeline: list[str]
    source: Literal["ai", "rules"]
    fallback_reason: str | None = None


SYSTEM_PROMPT = """You are a security analyst writing a short incident report.
You receive facts that a rule-based detector already confirmed.
Use only these facts. Do not invent times, users or IP addresses.
Reply with one JSON object and nothing else, with exactly these keys:
  "summary": 2-3 sentences explaining what happened,
  "attack_type": one of "brute_force", "password_spraying", "account_compromise",
  "mitre_technique": "T1110.001" for brute_force, "T1110.003" for
      password_spraying, "T1078" for account_compromise,
  "recommended_actions": a list of 1-5 short actions for the response team.
Use "account_compromise" only if success_after_failures is true."""


def collect_facts(analyzer, ip_address):
    """Everything the detector knows about one IP, plus its timeline."""
    facts = analyzer.analyze_ip(ip_address)

    facts["timeline"] = [
        f"{event.timestamp} {event.event_type} user={event.username}"
        for event in sorted(analyzer.events, key=lambda e: e.timestamp)
        if event.ip_address == ip_address
    ]
    return facts


def rule_attack_type(facts):
    if facts["success_after_failures"]:
        return "account_compromise"

    if len(facts["targeted_usernames"]) > 1:
        return "password_spraying"

    return "brute_force"


def rule_analysis(facts):
    """A plain, template-based report used when the model is not available."""
    attack_type = rule_attack_type(facts)
    users = ", ".join(facts["targeted_usernames"])

    summary = (
        f"{facts['ip_address']} made {facts['failed_attempts']} failed login "
        f"attempts against: {users}."
    )
    if facts["brute_force"]:
        summary += " The attempts came in a rapid burst, typical of a script."
    if facts["success_after_failures"]:
        summary += " A login then succeeded, so an account may be compromised."

    actions = [f"Block or rate-limit {facts['ip_address']} at the firewall."]
    if facts["success_after_failures"]:
        actions.append("Reset the password of the account that logged in "
                       "and end its active sessions.")
    actions.append(f"Review recent activity for: {users}.")
    actions.append("Enable multi-factor authentication on targeted accounts.")

    return AIIncidentAnalysis(
        summary=summary,
        attack_type=attack_type,
        mitre_technique=TECHNIQUES[attack_type][0],
        recommended_actions=actions,
    )


def check_grounded(analysis, facts):
    """Reject claims the detector's facts do not support."""
    if (analysis.attack_type == "account_compromise"
            and not facts["success_after_failures"]):
        raise ValueError("account_compromise needs a successful login "
                         "after failures, and there was none")


def build_user_prompt(facts, previous_error=None):
    # The facts are sent as JSON data, separate from the instructions.
    prompt = "Facts:\n" + json.dumps(facts, indent=2)

    if previous_error:
        prompt += (f"\n\nYour previous answer was rejected: {previous_error}\n"
                   "Return corrected JSON.")
    return prompt


def ask_model(llm, facts):
    """Ask the model, validate the answer, retry once. Raises on failure."""
    error = None

    for _ in range(MAX_ATTEMPTS):
        try:
            raw = llm.complete(SYSTEM_PROMPT, build_user_prompt(facts, error))
            analysis = AIIncidentAnalysis.model_validate_json(raw)
            check_grounded(analysis, facts)
            return analysis

        except ValidationError as problem:
            # Keep only the short messages, not the whole Pydantic dump
            error = "; ".join(item["msg"] for item in problem.errors())
        except ValueError as problem:
            error = str(problem)

    raise ValueError(error)


def generate_incident_report(analyzer, ip_address, llm=None):
    facts = collect_facts(analyzer, ip_address)

    source = "rules"
    fallback_reason = None

    if llm is None:
        analysis = rule_analysis(facts)
        fallback_reason = "AI is switched off"
    else:
        try:
            analysis = ask_model(llm, facts)
            source = "ai"
        except LLMError as error:
            analysis = rule_analysis(facts)
            fallback_reason = str(error)
        except ValueError as error:
            analysis = rule_analysis(facts)
            fallback_reason = f"AI answer failed validation twice: {error}"

    return IncidentReport(
        **analysis.model_dump(),
        ip_address=ip_address,
        risk_level=facts["risk_level"],
        risk_score=facts["risk_score"],
        technique_name=TECHNIQUES[analysis.attack_type][1],
        timeline=facts["timeline"],
        source=source,
        fallback_reason=fallback_reason,
    )
