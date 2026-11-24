from grade_models import grade


def run(cx, kind, data):
    if kind != "grade_turn_factors":
        raise ValueError(kind)
    return grade(cx, data["piece"], data.get("evidence_version", 1))
