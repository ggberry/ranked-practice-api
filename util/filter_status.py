class FilterInfo:
    def __init__(self):
        self.enabled = False
        self.percentage = 0
        self.current = 0
        self.total = 0

    def get_status(self):
        if self.enabled:
            return f"Filter On.<br>Progress: {self.percentage}% ({self.current} / {self.total})"

        return "Filter Off"
