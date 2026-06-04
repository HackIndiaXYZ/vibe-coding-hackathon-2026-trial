from crewai import Agent, Task, Crew
from pydantic import BaseModel
from config import llm
from agents.utils import parse_json, llm_retry


class Assignment(BaseModel):
    title: str
    objective: str
    instructions: list[str]
    submission_format: str
    estimated_time: str


@llm_retry
def run_assignment_agent(
    topic: str,
    grade: str,
    subject: str,
    brief: str,
    difficulty_note: str,
) -> dict:
    agent = Agent(
        role="Assignment creator",
        goal="Design a meaningful assignment that reinforces learning and is achievable at the grade level",
        backstory=(
            "You are a curriculum developer who crafts assignments that challenge students "
            "appropriately, with clear step-by-step instructions and realistic time estimates"
        ),
        llm=llm,
        verbose=False,
    )

    task = Task(
        description=(
            f"Create one assignment for the following:\n"
            f"  Topic: {topic}\n"
            f"  Grade: {grade}\n"
            f"  Subject: {subject}\n"
            f"  Assignment brief: {brief}\n"
            f"  Difficulty note: {difficulty_note}\n\n"
            "Return ONLY a valid JSON object with exactly these keys: "
            "title (str), objective (str), instructions (list of str steps), "
            "submission_format (str), estimated_time (str). "
            "No extra text, no markdown fences."
        ),
        expected_output=(
            "A JSON object with keys: title, objective, instructions, submission_format, estimated_time"
        ),
        output_json=Assignment,
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()

    if result.json_dict:
        return result.json_dict
    return parse_json(result.raw)
