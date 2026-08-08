"""Analytics engine."""


def calculate_learning_health_score(academic_score: float, attendance_score: float, quiz_consistency: float, time_management: float, digital_wellness: float) -> float:
    return (academic_score * 0.5) + (attendance_score * 0.15) + (quiz_consistency * 0.15) + (time_management * 0.1) + (digital_wellness * 0.1)


def calculate_topic_difficulty(average_score: float) -> float:
    return max(0.0, 100.0 - average_score)


def rank_students(student_rows: list[dict]) -> list[dict]:
    return sorted(student_rows, key=lambda item: item.get("average_score", 0), reverse=True)
