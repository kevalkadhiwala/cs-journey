class LogEvent:
    def __init__(self, timestamp, ip_address, event_type, username):
        self.timestamp = timestamp
        self.ip_address = ip_address
        self.event_type = event_type
        self.username = username

events = []
with open("security.log", "r") as file:
    for line in file:
        parts = line.strip().split("|")
        event = LogEvent(parts[0], parts[1], parts[2], parts[3])
        events.append(event)

print(f"Total events: {len(events)}")

#print(failed_events)        

class LogAnalyzer:

    def __init__(self, events):
        self.events = events 

    def count_failed_logins(self):
        failed_events = {}

        for event in self.events:

            if event.event_type == "LOGIN_FAILED":
                if event.ip_address not in failed_events:
                    failed_events[event.ip_address] = 1
                else:
                    failed_events[event.ip_address] += 1

        return failed_events

    def detect_suspicious_ips(self, threshold=3):

        suspicious_ips = []
        failed_events = self.count_failed_logins()

        for ip, count in failed_events.items():
            if count >= threshold:
                suspicious_ips.append(ip)
                
        return suspicious_ips 

analyzer = LogAnalyzer(events)

print(analyzer.count_failed_logins())
print(analyzer.detect_suspicious_ips())