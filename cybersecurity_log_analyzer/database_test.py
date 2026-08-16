import sqlite3

connection = sqlite3.connect("security.db")

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_events (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        ip_address TEXT,
        event_type TEXT,
        username TEXT
    )
""")

cursor.execute("""
    INSERT INTO security_events
    (timestamp, ip_address, event_type, username)
    VALUES
    ('2026-08-16 10:00:00', '192.168.1.50', 'LOGIN_SUCCESS', 'keval'),
    ('2026-08-16 10:01:15', '192.168.1.99', 'LOGIN_FAILED', 'unknown')    
""")

connection.commit()

cursor.execute("""
    SELECT COUNT(*)
    FROM security_events
    WHERE event_type = 'LOGIN_FAILED' AND ip_address = '192.168.1.99';
""")

rows = cursor.fetchone()

for row in rows:
    print(row)

connection.close()