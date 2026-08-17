class LogEvent:

    def __init__(self, timestamp, ip_address, event_type, username):
        self.timestamp = timestamp
        self.ip_address = ip_address
        self.event_type = event_type
        self.username = username