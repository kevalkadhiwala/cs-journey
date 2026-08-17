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
        failed_events = self.count_failed_logins()
        suspicious_ips = []

        for ip, count in failed_events.items():
            if count >= threshold:
                suspicious_ips.append(ip)

        return suspicious_ips