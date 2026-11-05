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
        "LOGIN_SUCCESS": 3, "LOGIN_FAILED": 10, "LOGOUT": 1
    }


def test_recent_events_newest_first(loaded_db):
    recent = loaded_db.get_recent_events(limit=2)
    assert [e.timestamp for e in recent] == ["2026-08-18 11:23:00", "2026-08-18 11:21:30"]


def test_filter_by_date_range(loaded_db):
    events = loaded_db.get_events_filtered(start="2026-08-18 09:00:00",
                                           end="2026-08-18 09:59:59")
    assert len(events) == 8
    assert all(e.timestamp.startswith("2026-08-18 09:") for e in events)


def test_filtered_events_are_newest_first(loaded_db):
    events = loaded_db.get_events_filtered(event_type="LOGIN_FAILED")
    timestamps = [e.timestamp for e in events]
    assert timestamps == sorted(timestamps, reverse=True)


def test_pagination_returns_separate_pages(loaded_db):
    first_page = loaded_db.get_events_filtered(limit=5, offset=0)
    second_page = loaded_db.get_events_filtered(limit=5, offset=5)
    assert len(first_page) == 5 and len(second_page) == 5
    first_times = {e.timestamp for e in first_page}
    assert not first_times & {e.timestamp for e in second_page}


def test_count_matches_filters(loaded_db):
    assert loaded_db.count_events_filtered() == 14
    assert loaded_db.count_events_filtered(event_type="LOGIN_FAILED") == 10
    assert loaded_db.count_events_filtered(start="2026-08-18 11:00:00") == 5
