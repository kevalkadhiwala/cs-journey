from datetime import datetime, timedelta

import pytest

from app import demo_logs
from app.ingest import main, parse_line
from app.log_analyzer import LogAnalyzer

NOW = datetime(2026, 11, 10, 15, 30, 0)


@pytest.fixture
def analyzer():
    events = [parse_line(line) for line in demo_logs.generate(now=NOW)]
    return LogAnalyzer(events)


def test_every_line_parses_and_sits_in_the_last_24_hours():
    lines = demo_logs.generate(now=NOW)

    for line in lines:
        event = parse_line(line)
        assert event is not None, line
        time = datetime.strptime(event.timestamp, "%Y-%m-%d %H:%M:%S")
        assert NOW - timedelta(hours=24) <= time <= NOW

    assert lines == sorted(lines)


def test_same_seed_same_log_and_times_follow_the_clock():
    assert demo_logs.generate(now=NOW) == demo_logs.generate(now=NOW)
    assert demo_logs.generate(now=NOW) != demo_logs.generate(now=NOW, random_seed=7)

    later = demo_logs.generate(now=NOW + timedelta(days=1))
    assert later[0].startswith("2026-11-10")


def test_only_the_attackers_are_flagged(analyzer):
    # Office staff mistype a password now and then, but never get flagged
    assert sorted(analyzer.detect_suspicious_ips()) == sorted([
        demo_logs.BRUTE_FORCE_IP, demo_logs.SPRAYING_IP, demo_logs.COMPROMISE_IP,
        demo_logs.SLOW_GUESSING_IP, demo_logs.INJECTION_IP,
    ])


@pytest.mark.parametrize("ip, risk_level, brute_force, compromised", [
    (demo_logs.BRUTE_FORCE_IP, "MEDIUM", True, False),
    (demo_logs.SPRAYING_IP, "HIGH", True, False),
    (demo_logs.COMPROMISE_IP, "HIGH", True, True),
    (demo_logs.SLOW_GUESSING_IP, "LOW", False, False),
    (demo_logs.INJECTION_IP, "LOW", False, False),
])
def test_each_attack_is_detected_as_planned(analyzer, ip, risk_level,
                                            brute_force, compromised):
    facts = analyzer.analyze_ip(ip)

    assert facts["risk_level"] == risk_level
    assert facts["brute_force"] is brute_force
    assert facts["success_after_failures"] is compromised


def test_botnet_is_caught_per_account_not_per_ip(analyzer):
    assert not set(demo_logs.BOTNET_IPS) & set(analyzer.detect_suspicious_ips())
    assert analyzer.detect_distributed_attack("finance")
    assert analyzer.find_targeted_accounts() == ["finance"]


def test_ingest_demo_loads_the_generated_log(tmp_path, capsys):
    main(["--demo", "--db", str(tmp_path / "demo.db")])

    output = capsys.readouterr().out
    assert "from the demo log generator (0 malformed lines skipped)" in output
    assert demo_logs.COMPROMISE_IP in output
