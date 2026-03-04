from flask import abort
from datetime import datetime


class FilterInfo:
    def __init__(self):
        self.max_timeout = 60
        self.required = {"current": int, "total": int}
        self.progress_data = {}  # Format: {"127.0.0.1": {"enabled": True, "current": 60, "total": 100, "timestamp": ...}, ...}

    def get_status(self):
        header = '<head><meta name="format-detection" content="telephone=no, email=no, address=no" /></head><span style="font-family: Consolas; font-size: 16px;">'
        status_display = "Ranked Practice Filter.<br><br>"
        number = 0

        to_remove = []

        for ip, data in self.progress_data.items():
            timestamp = data["timestamp"]
            timedelta = (datetime.now() - timestamp).total_seconds()

            if timedelta > self.max_timeout:
                to_remove.append(ip)
                continue

            current = data["current"]
            total = data["total"]

            status_display += (f"Filter #{number + 1}"
                               f" - Progress: {current / total * 100:.1f}% ({current}/{total}) | Timeout in: {(self.max_timeout - timedelta):.0f}s | IP Address: {ip}<br>")
            number += 1

        for ip in to_remove:
            del self.progress_data[ip]

        return header + status_display + "</span>"

    def status_update(self, ip, data):
        for key in data.keys():
            item = self.required.get(key)

            if not item or not isinstance(data[key], self.required[key]):
                abort(400, description="Invalid request")

        self.progress_data[ip] = {
            "current": data["current"],
            "total": data["total"],
            "timestamp": datetime.now()
        }
