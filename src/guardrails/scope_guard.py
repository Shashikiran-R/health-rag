import re

PROHIBITED_PATTERNS = [
    # Medical advice
    r"\b(diagnose|diagnos|prescribe|prescri|medication|treatment|symptom|disease|cure)\b",
    # Calorie / weight targets
    r"\b(calorie target|caloric target|how many calories|lose weight|gain weight)\b",
    r"\b(bmi|body mass index|ideal weight|target weight|weight goal)\b",
    # Personal medical
    r"\b(should i take|am i sick|do i have|my doctor)\b",
]

class ScopeGuard:
    def is_out_of_scope(self, query: str) -> bool:
        """Hard-coded guardrail. Returns True if query is in a prohibited category."""
        query_lower = query.lower()
        return any(re.search(p, query_lower) for p in PROHIBITED_PATTERNS)
