from crewai import Agent, Task, Crew
from pydantic import BaseModel
from config import llm
from agents.utils import parse_json, llm_retry


class LessonPlan(BaseModel):
    slides_brief: str
    quiz_brief: str
    assignment_brief: str
    rubric_brief: str
    faq_brief: str
    difficulty_note: str


@llm_retry
def run_orchestrator(
    topic: str,
    grade: str,
    subject: str,
    struggle_areas: list[str],
) -> dict:
    planner = Agent(
        role="Expert curriculum designer",
        goal="Break down a teaching topic into 5 structured lesson components",
        backstory=(
            "You are an experienced teacher who designs lessons tailored to "
            "specific grade levels and student weaknesses"
        ),
        llm=llm,
        verbose=False,
    )

    struggle_text = ", ".join(struggle_areas) if struggle_areas else "none specified"

    task = Task(
        description=(
            f"Design a structured lesson plan for the following:\n"
            f"  Topic: {topic}\n"
            f"  Grade: {grade}\n"
            f"  Subject: {subject}\n"
            f"  Student struggle areas: {struggle_text}\n\n"
            "Return ONLY a valid JSON object with exactly these keys: "
            "slides_brief, quiz_brief, assignment_brief, rubric_brief, "
            "faq_brief, difficulty_note. No extra text, no markdown fences."
        ),
        expected_output=(
            "A JSON object with keys: slides_brief, quiz_brief, "
            "assignment_brief, rubric_brief, faq_brief, difficulty_note"
        ),
        output_json=LessonPlan,
        agent=planner,
    )

    crew = Crew(agents=[planner], tasks=[task], verbose=False)
    result = crew.kickoff()

    if result.json_dict:
        return result.json_dict
    return parse_json(result.raw)
