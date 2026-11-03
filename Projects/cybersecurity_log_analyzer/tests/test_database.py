from app.log_event import LogEvent


def test_events_round_trip(loaded_db, sample_events):
    stored = loaded_db.get_events()
    assert len(stored) == len(sample_events)
    assert stored[0].username == "keval"


def test_duplicate_events_are_ignored(db):
    event = LogEvent("2026-08-18 09:00:00", "10.0.0.1", "LOGIN_FAILED", "admin")
    db.insert_event(event)
    db.insert_event(event)
    assert len(db.get_events()) == 1


def test_find_suspicious_ips_sql(loaded_db):
    assert loaded_db.find_suspicious_ips() == [("192.168.1.99", 4), ("192.168.1.77", 3)]


def test_filter_by_ip_and_type(loaded_db):
    events = loaded_db.get_events_filtered(ip_address="192.168.1.99",
                                           event_type="LOGIN_FAILED")
    assert len(events) == 4
    assert all(e.ip_address == "192.168.1.99" for e in events)


def test_filter_input_is_not_injected_into_sql(loaded_db):
    # Parameterised queries treat this as a plain value, not SQL
    events = loaded_db.get_events_filtered(ip_address="' OR '1'='1")
    assert events == []


def test_statistics(loaded_db):
    assert loaded_db.get_event_statistics() == {
        "LOGIN_SUCCESS": 3, "LOGIN_FAILED": 7, "LOGOUT": 1
    }


def test_recent_events_newest_first(loaded_db):
    recent = loaded_db.get_recent_events(limit=2)
    assert [e.timestamp for e in recent] == ["2026-08-18 11:15:00", "2026-08-18 11:00:00"]
