import sqlite3
from log_event import LogEvent

class DatabaseManager:

    def __init__(self, database_name):
        self.database_name = database_name

    def connect(self):
        return sqlite3.connect(self.database_name)

    def create_table(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                ip_address TEXT,
                event_type TEXT,
                username TEXT,
                UNIQUE(timestamp, ip_address, event_type, username)
            )     
        """)

        connection.commit()
        connection.close()

    def insert_event(self, event):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO security_events
            (timestamp, ip_address, event_type, username)
            VALUES (?, ?, ?, ?)
        """, (
            event.timestamp,
            event.ip_address,
            event.event_type,
            event.username
        ))

        connection.commit()
        connection.close()

    def get_events(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT timestamp, ip_address, event_type, username
            FROM security_events
        """)

        rows = cursor.fetchall()
        connection.close()

        events = []

        for row in rows:
            event = LogEvent(
                row[0],
                row[1],
                row[2],
                row[3]
            )

            events.append(event)

        return events

    def get_events_by_ip(self, ip_address):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT timestamp, ip_address, event_type, username
            FROM security_events
            WHERE ip_address = ?
        """, (ip_address,))

        rows = cursor.fetchall()

        connection.close()

        events = []

        for row in rows:
            event = LogEvent(
                row[0],
                row[1],
                row[2],
                row[3]
            )

            events.append(event)

        return events
    def find_suspicious_ips(self, threshold=3):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT ip_address, COUNT(*)
            FROM security_events
            WHERE event_type = 'LOGIN_FAILED'
            GROUP BY ip_address
            HAVING COUNT(*) >= ?
            ORDER BY COUNT(*) DESC
        """, (threshold,))

        rows = cursor.fetchall()
        connection.close()

        return rows
