class TagManager:
    def __init__(self):
        self.tags = []

    def add(self, timestamp):
        self.tags.append(timestamp)

    def remove_last(self):
        if self.tags:
            self.tags.pop()

    def clear(self):
        self.tags = []

    def get_last_tag_label(self):
        if not self.tags:
            return ""
        tag_type = "Inicio" if len(self.tags) % 2 != 0 else "Fin"
        clip_num = (len(self.tags) + 1) // 2
        t = self.tags[-1]
        return f"Clip {clip_num} - {tag_type}: {t:.2f}s"
