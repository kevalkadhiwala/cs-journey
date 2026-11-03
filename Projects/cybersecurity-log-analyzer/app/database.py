import sqlite3
from app.log_event import LogEvent

class DatabaseManager:

    def __init__(self, database_name):
        # Accepts a string or a pathlib.Path
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

    def get_events_filtered(self, ip_address=None, event_type=None):

        connection = self.connect()
        cursor = connection.cursor()

        query = """
            SELECT timestamp, ip_address, event_type, username
            FROM security_events
        """

        conditions = []
        values = []

        if ip_address:
            conditions.append("ip_address = ?")
            values.append(ip_address)

        if event_type:
            conditions.append("event_type = ?")
            values.append(event_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, values)

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

    def get_event_statistics(self):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT event_type, COUNT(*)
            FROM security_events
            GROUP BY event_type
        """)

        rows = cursor.fetchall()

        connection.close()

        statistics = {}

        for row in rows:
            statistics[row[0]] = row[1]

        return statistics

    def get_recent_events(self, limit=10):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT timestamp, ip_address, event_type, username
            FROM security_events
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

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