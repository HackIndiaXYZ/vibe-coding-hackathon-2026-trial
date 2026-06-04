from crewai import Agent, Task, Crew
from pydantic import BaseModel
from config import llm
from agents.utils import parse_json, llm_retry


class FAQ(BaseModel):
    question: str
    answer: str


class FAQList(BaseModel):
    faqs: list[FAQ]


@llm_retry
def run_faq_agent(
    topic: str,
    grade: str,
    subject: str,
    brief: str,
    difficulty_note: str,
) -> list:
    agent = Agent(
        role="Student FAQ anticipator",
        goal="Anticipate the 10 most common student questions and provide grade-appropriate answers",
        backstory=(
            "You are a seasoned classroom teacher with an intuitive sense of what confuses "
            "students at each grade level, and a talent for explaining things simply and clearly"
        ),
        llm=llm,
        verbose=False,
    )

    task = Task(
        description=(
            f"Generate 10 student FAQs for the following:\n"
            f"  Topic: {topic}\n"
            f"  Grade: {grade}\n"
            f"  Subject: {subject}\n"
            f"  FAQ brief: {brief}\n"
            f"  Difficulty note: {difficulty_note}\n\n"
            "Return ONLY a valid JSON array of exactly 10 FAQ objects, each with keys: "
            "question (str) and answer (str). Answers must be simple and appropriate for "
            f"{grade} students. No extra text, no markdown fences."
        ),
        expected_output=(
            "A JSON array of 10 objects with keys: question, answer"
        ),
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()

    return parse_json(result.raw)
