from app.log_analyzer import LogAnalyzer
from tests.conftest import make_events


def test_counts_failed_logins_per_ip(sample_events):
    counts = LogAnalyzer(sample_events).count_failed_logins()
    assert counts == {"192.168.1.99": 4, "192.168.1.77": 3,
                      "203.0.113.10": 1, "203.0.113.11": 1, "203.0.113.12": 1}


def test_suspicious_ips_use_threshold(sample_events):
    analyzer = LogAnalyzer(sample_events)
    assert set(analyzer.detect_suspicious_ips()) == {"192.168.1.99", "192.168.1.77"}
    assert analyzer.detect_suspicious_ips(threshold=4) == ["192.168.1.99"]


def test_two_failures_are_not_suspicious():
    events = make_events([
        ("2026-08-18 09:00:00", "10.0.0.1", "LOGIN_FAILED", "admin"),
        ("2026-08-18 09:00:05", "10.0.0.1", "LOGIN_FAILED", "admin"),
    ])
    assert LogAnalyzer(events).detect_suspicious_ips() == []


def test_brute_force_needs_failures_close_together(sample_events):
    analyzer = LogAnalyzer(sample_events)
    # 3 failures within 6 seconds
    assert analyzer.detect_brute_force("192.168.1.99") is True
    # 3 failures spread over 80 minutes
    assert analyzer.detect_brute_force("192.168.1.77") is False


def test_brute_force_works_on_unsorted_events():
    events = make_events([
        ("2026-08-18 09:00:40", "10.0.0.2", "LOGIN_FAILED", "root"),
        ("2026-08-18 09:00:00", "10.0.0.2", "LOGIN_FAILED", "root"),
        ("2026-08-18 09:00:20", "10.0.0.2", "LOGIN_FAILED", "root"),
    ])
    assert LogAnalyzer(events).detect_brute_force("10.0.0.2") is True


def test_success_after_failures(sample_events):
    analyzer = LogAnalyzer(sample_events)
    assert analyzer.detect_success_after_failures("192.168.1.99") is True
    assert analyzer.detect_success_after_failures("192.168.1.50") is False


def test_success_resets_the_failure_count():
    events = make_events([
        ("2026-08-18 09:00:00", "10.0.0.3", "LOGIN_FAILED", "a"),
        ("2026-08-18 09:00:01", "10.0.0.3", "LOGIN_FAILED", "a"),
        ("2026-08-18 09:00:02", "10.0.0.3", "LOGIN_SUCCESS", "a"),
        ("2026-08-18 09:00:03", "10.0.0.3", "LOGIN_FAILED", "a"),
        ("2026-08-18 09:00:04", "10.0.0.3", "LOGIN_SUCCESS", "a"),
    ])
    assert LogAnalyzer(events).detect_success_after_failures("10.0.0.3") is False


def test_targeted_usernames_are_unique(sample_events):
    analyzer = LogAnalyzer(sample_events)
    assert analyzer.get_targeted_usernames("192.168.1.99") == ["admin", "keval"]


def test_risk_score_high_when_every_rule_fires(sample_events):
    # 4 failures (+2), brute force (+3), 2 usernames (+2), success after failures (+3)
    assert LogAnalyzer(sample_events).calculate_risk("192.168.1.99") == (10, "HIGH")


def test_risk_score_low_for_slow_failures(sample_events):
    # only the "3 or more failures" rule fires (+2)
    assert LogAnalyzer(sample_events).calculate_risk("192.168.1.77") == (2, "LOW")


def test_analyze_ip_report(sample_events):
    report = LogAnalyzer(sample_events).analyze_ip("192.168.1.99")
    assert report == {
        "ip_address": "192.168.1.99",
        "failed_attempts": 4,
        "targeted_usernames": ["admin", "keval"],
        "brute_force": True,
        "success_after_failures": True,
        "risk_score": 10,
        "risk_level": "HIGH",
    }


def test_empty_log_produces_no_findings():
    analyzer = LogAnalyzer([])
    assert analyzer.detect_suspicious_ips() == []
    assert analyzer.calculate_risk("1.2.3.4") == (0, "LOW")


# ------------------------------------------------------------
# Distributed attacks: many IPs against one account
# ------------------------------------------------------------

def test_distributed_attack_detected_in_sample(sample_events):
    analyzer = LogAnalyzer(sample_events)
    assert analyzer.detect_distributed_attack("root") is True
    # admin and keval were only attacked from one IP
    assert analyzer.detect_distributed_attack("admin") is False
    assert analyzer.find_targeted_accounts() == ["root"]


def test_distributed_attack_needs_ips_close_together():
    events = make_events([
        ("2026-08-18 09:00:00", "10.0.0.1", "LOGIN_FAILED", "admin"),
        ("2026-08-18 09:30:00", "10.0.0.2", "LOGIN_FAILED", "admin"),
        ("2026-08-18 10:00:00", "10.0.0.3", "LOGIN_FAILED", "admin"),
    ])
    assert LogAnalyzer(events).detect_distributed_attack("admin") is False


def test_one_ip_failing_many_times_is_not_distributed():
    events = make_events([
        ("2026-08-18 09:00:00", "10.0.0.1", "LOGIN_FAILED", "admin"),
        ("2026-08-18 09:00:05", "10.0.0.1", "LOGIN_FAILED", "admin"),
        ("2026-08-18 09:00:10", "10.0.0.1", "LOGIN_FAILED", "admin"),
        ("2026-08-18 09:00:15", "10.0.0.1", "LOGIN_FAILED", "admin"),
    ])
    assert LogAnalyzer(events).detect_distributed_attack("admin") is False


def test_distributed_attack_finds_window_later_in_log():
    # The first IP is too early, but the last three fit inside 10 minutes
    events = make_events([
        ("2026-08-18 08:00:00", "10.0.0.9", "LOGIN_FAILED", "admin"),
        ("2026-08-18 09:00:00", "10.0.0.1", "LOGIN_FAILED", "admin"),
        ("2026-08-18 09:04:00", "10.0.0.2", "LOGIN_FAILED", "admin"),
        ("2026-08-18 09:09:00", "10.0.0.3", "LOGIN_FAILED", "admin"),
    ])
    assert LogAnalyzer(events).detect_distributed_attack("admin") is True


def test_successful_logins_do_not_count_as_attacks():
    events = make_events([
        ("2026-08-18 09:00:00", "10.0.0.1", "LOGIN_SUCCESS", "admin"),
        ("2026-08-18 09:01:00", "10.0.0.2", "LOGIN_SUCCESS", "admin"),
        ("2026-08-18 09:02:00", "10.0.0.3", "LOGIN_SUCCESS", "admin"),
    ])
    analyzer = LogAnalyzer(events)
    assert analyzer.detect_distributed_attack("admin") is False
    assert analyzer.find_targeted_accounts() == []


def test_analyze_account_report(sample_events):
    assert LogAnalyzer(sample_events).analyze_account("root") == {
        "username": "root",
        "failed_attempts": 3,
        "attacking_ips": ["203.0.113.10", "203.0.113.11", "203.0.113.12"],
        "distributed_attack": True,
    }


def test_empty_log_has_no_targeted_accounts():
    assert LogAnalyzer([]).find_targeted_accounts() == []
