from typing import List, Tuple


class GradePolicy:
    # A list of (threshold_score, grade_string) from highest to lowest
    DEFAULT: List[Tuple[float, str]] = [
        (100.0, "A+"),
        (95.0, "A"),
        (90.0, "B"),
        (80.0, "C"),
        (0.0, "Failed"),
    ]

    @classmethod
    def resolve_grade(cls, score: float, policy: List[Tuple[float, str]] = None) -> str:
        policy = policy or cls.DEFAULT
        for threshold, grade in policy:
            if score >= threshold:
                return grade
        return "Failed"
