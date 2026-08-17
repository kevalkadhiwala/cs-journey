from log_event import LogEvent
from database import DatabaseManager

db = DatabaseManager("security.db")
db.create_table()


with open("security.log", "r") as file:
    for line in file:
        parts = line.strip().split("|")
        event = LogEvent(parts[0], parts[1], parts[2], parts[3])

        db.insert_event(event)

