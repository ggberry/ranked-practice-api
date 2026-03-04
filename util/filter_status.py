from flask import abort


class FilterInfo:
    def __init__(self):
        self.required = {"current": int, "total": int}
        self.progress_data = {}  # Format: {"127.0.0.1": {"enabled": True, "current": 60, "total": 100}, ...}

    def get_status(self):
        header = '<head><meta name="format-detection" content="telephone=no, email=no, address=no" /></head><span style="font-family: Consolas; font-size: 16px;">'
        status_display = "Ranked Practice Filter.<br><br>"
        index = 0

        for ip, data in self.progress_data.items():
            current = data["current"]
            total = data["total"]

            status_display += (f"Filter #{index + 1} - {ip}"
                               f" | Progress: {current / total * 100:.1f}% ({current}/{total})")
            index += 1

        return header + status_display + "</span>"

    def status_update(self, ip, data):
        for key in data.keys():
            item = self.required.get(key)

            if not item or not isinstance(data[key], self.required[key]):
                abort(400, description="Invalid request")

        self.progress_data[ip] = {
            "current": data["current"],
            "total": data["total"],
        }
