from datetime import datetime

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

    def get_targeted_usernames(self, ip_address):
        usernames = []

        for event in self.events:
            if event.ip_address == ip_address:
                if event.username not in usernames:
                    usernames.append(event.username)

        return usernames

    def parse_timestamp(self, timestamp):
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    def detect_brute_force(self, ip_address, max_seconds=60, threshold=3):

        failed_events = []

        for event in self.events:
            if event.ip_address == ip_address and event.event_type == "LOGIN_FAILED":
                failed_events.append(event)

        failed_events.sort(key=lambda event: self.parse_timestamp(event.timestamp))

        for i in range(len(failed_events) - threshold + 1):

            first_event = self.parse_timestamp(failed_events[i].timestamp)

            last_event = self.parse_timestamp(failed_events[i + threshold - 1].timestamp)

            time_difference = (last_event - first_event).total_seconds()

            if time_difference <= max_seconds:
                return True

        return False 

    def detect_success_after_failures(self, ip_address, threshold=3):

        events = []

        for event in self.events:
            if event.ip_address == ip_address:
                events.append(event)

        events.sort(key=lambda event: self.parse_timestamp(event.timestamp))

        failed_count = 0

        for event in events:

            if event.event_type == "LOGIN_FAILED":
                failed_count += 1

            elif event.event_type == "LOGIN_SUCCESS":

                if failed_count >= threshold:
                    return True

                failed_count = 0
        return False

    def calculate_risk(self, ip_address):

        failed_logins = self.count_failed_logins()

        failed_count = failed_logins.get(ip_address, 0)

        usernames = self.get_targeted_usernames(ip_address)

        brute_force = self.detect_brute_force(ip_address)

        success_after_failures = self.detect_success_after_failures(ip_address)

        score = 0

        if failed_count >= 3:
            score += 2

        if brute_force:
            score += 3

        if len(usernames) > 1:
            score += 2

        if success_after_failures:
            score += 3

        if score >= 6:
            risk = "HIGH"
        elif score >= 3:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return score, risk

    def analyze_ip(self, ip_address):

        failed_logins = self.count_failed_logins()
        failed_count = failed_logins.get(ip_address, 0)

        usernames = self.get_targeted_usernames(ip_address)

        brute_force = self.detect_brute_force(ip_address)

        success_after_failures = self.detect_success_after_failures(ip_address)

        score, risk = self.calculate_risk(ip_address)

        return {
            "ip_address": ip_address,
            "failed_attempts": failed_count,
            "targeted_usernames": usernames,
            "brute_force": brute_force,
            "success_after_failures": success_after_failures,
            "risk_score": score,
            "risk_level": risk
        }