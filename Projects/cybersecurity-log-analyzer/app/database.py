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

    def _build_filters(self, ip_address=None, event_type=None,
                       start=None, end=None):
        # Builds the WHERE clause and its values for the filter methods.
        # Values are always passed as ? parameters, never put into the SQL.
        conditions = []
        values = []

        if ip_address:
            conditions.append("ip_address = ?")
            values.append(ip_address)

        if event_type:
            conditions.append("event_type = ?")
            values.append(event_type)

        # Timestamps are stored as "YYYY-MM-DD HH:MM:SS" text, which sorts
        # in date order, so plain text comparison works for date ranges.
        if start:
            conditions.append("timestamp >= ?")
            values.append(start)

        if end:
            conditions.append("timestamp <= ?")
            values.append(end)

        where = ""

        if conditions:
            where = " WHERE " + " AND ".join(conditions)

        return where, values

    def get_events_filtered(self, ip_address=None, event_type=None,
                            start=None, end=None, limit=None, offset=0):

        connection = self.connect()
        cursor = connection.cursor()

        where, values = self._build_filters(ip_address, event_type, start, end)

        query = """
            SELECT timestamp, ip_address, event_type, username
            FROM security_events
        """ + where + " ORDER BY timestamp DESC, id DESC"

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            values = values + [limit, offset]

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

    def count_events_filtered(self, ip_address=None, event_type=None,
                              start=None, end=None):

        connection = self.connect()
        cursor = connection.cursor()

        where, values = self._build_filters(ip_address, event_type, start, end)

        cursor.execute("SELECT COUNT(*) FROM security_events" + where, values)

        total = cursor.fetchone()[0]

        connection.close()

        return total

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