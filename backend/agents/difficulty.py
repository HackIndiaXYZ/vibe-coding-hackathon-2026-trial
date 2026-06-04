BRIEF_KEYS = ["slides_brief", "quiz_brief", "assignment_brief", "rubric_brief", "faq_brief"]


def enrich_briefs(orchestrator_output: dict, struggle_areas: list[str], grade: str) -> dict:
    enriched = orchestrator_output.copy()

    if struggle_areas:
        areas_str = ", ".join(struggle_areas)
        calibration = (
            f" Note: Students in this class are specifically struggling with: {areas_str}."
            " Adjust the content to add extra scaffolding, simpler explanations,"
            " and reinforce these concepts more than others."
        )
        for key in BRIEF_KEYS:
            if key in enriched:
                enriched[key] = enriched[key] + calibration

        enriched["difficulty_note"] = (
            f"Difficulty calibrated for grade {grade}."
            f" Weak areas: {areas_str}."
            " Prefer simpler language, more examples, and step-by-step explanations"
            " for these concepts."
        )

    return enriched
