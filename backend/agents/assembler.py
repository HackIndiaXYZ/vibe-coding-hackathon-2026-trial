from datetime import datetime, timezone
from config import supabase


def assemble_lesson(
    topic: str,
    grade: str,
    subject: str,
    slides: list,
    quiz: list,
    assignment: dict,
    rubric: list,
    faq: list,
) -> dict:
    generated_at = datetime.now(timezone.utc).isoformat()

    pack = {
        "topic": topic,
        "grade": grade,
        "subject": subject,
        "generated_at": generated_at,
        "slides": slides,
        "quiz": quiz,
        "assignment": assignment,
        "rubric": rubric,
        "faq": faq,
    }

    response = (
        supabase.table("lessons")
        .insert({
            "topic": topic,
            "grade": grade,
            "subject": subject,
            "generated_at": generated_at,
            "pack": pack,
        })
        .execute()
    )

    lesson_id = response.data[0]["id"]
    return {**pack, "lesson_id": lesson_id}
