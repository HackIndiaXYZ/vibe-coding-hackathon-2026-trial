from crewai import Agent, Task, Crew
from pydantic import BaseModel
from config import llm
from agents.utils import parse_json, llm_retry


class MCQ(BaseModel):
    question: str
    options: list[str]
    answer: str
    explanation: str


class QuizDeck(BaseModel):
    questions: list[MCQ]


@llm_retry
def run_quiz_agent(
    topic: str,
    grade: str,
    subject: str,
    brief: str,
    difficulty_note: str,
) -> list:
    agent = Agent(
        role="Assessment designer",
        goal="Create 10 multiple-choice questions that accurately test student understanding",
        backstory=(
            "You are an experienced assessment specialist who writes MCQs that are "
            "clear, unambiguous, and calibrated to the right difficulty for the grade level"
        ),
        llm=llm,
        verbose=False,
    )

    task = Task(
        description=(
            f"Generate 10 multiple-choice questions for the following:\n"
            f"  Topic: {topic}\n"
            f"  Grade: {grade}\n"
            f"  Subject: {subject}\n"
            f"  Quiz brief: {brief}\n"
            f"  Difficulty note: {difficulty_note}\n\n"
            "Return ONLY a valid JSON array of exactly 10 MCQ objects, each with keys: "
            "question (str), options (list of 4 strings formatted as 'A) ...', 'B) ...', 'C) ...', 'D) ...'), "
            "answer (str, one of 'A', 'B', 'C', 'D'), explanation (str). "
            "No extra text, no markdown fences."
        ),
        expected_output=(
            "A JSON array of 10 objects with keys: question, options, answer, explanation"
        ),
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()

    return parse_json(result.raw)
