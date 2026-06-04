from crewai import Agent, Task, Crew
from pydantic import BaseModel
from config import llm
from agents.utils import parse_json, llm_retry


class RubricCriterion(BaseModel):
    criterion: str
    excellent: str
    good: str
    needs_improvement: str


class Rubric(BaseModel):
    criteria: list[RubricCriterion]


@llm_retry
def run_rubric_agent(
    topic: str,
    grade: str,
    subject: str,
    brief: str,
    difficulty_note: str,
) -> list:
    agent = Agent(
        role="Grading rubric specialist",
        goal="Create a fair and detailed grading rubric with 4-5 criteria",
        backstory=(
            "You are an expert in educational assessment who designs rubrics that give "
            "students clear expectations and teachers consistent grading standards"
        ),
        llm=llm,
        verbose=False,
    )

    task = Task(
        description=(
            f"Create a grading rubric for the following:\n"
            f"  Topic: {topic}\n"
            f"  Grade: {grade}\n"
            f"  Subject: {subject}\n"
            f"  Rubric brief: {brief}\n"
            f"  Difficulty note: {difficulty_note}\n\n"
            "Return ONLY a valid JSON array of 4-5 criterion objects, each with keys: "
            "criterion (str), excellent (str), good (str), needs_improvement (str). "
            "No extra text, no markdown fences."
        ),
        expected_output=(
            "A JSON array of 4-5 objects with keys: criterion, excellent, good, needs_improvement"
        ),
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()

    return parse_json(result.raw)
