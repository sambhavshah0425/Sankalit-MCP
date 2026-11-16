class Intent:

    def __init__(self, template: str):
        self.template = template


class PromptAnalyzer:

    @staticmethod
    def analyze(text: str) -> Intent:
        """
        Analyzes prompt/filename text to classify the document template type.
        """
        normalized = text.lower()
        if "minutes" in normalized or "meeting" in normalized or "mom" in normalized:
            return Intent("meeting_minutes")
        elif "presentation" in normalized or "slides" in normalized or "ppt" in normalized:
            return Intent("presentation")
        elif "proposal" in normalized or "tender" in normalized:
            return Intent("proposal")
        else:
            return Intent("technical_report")
