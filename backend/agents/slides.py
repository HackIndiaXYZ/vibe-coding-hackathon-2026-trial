from crewai import Agent, Task, Crew
from pydantic import BaseModel
from config import llm
from agents.utils import parse_json, llm_retry


class Slide(BaseModel):
    slide_number: int
    title: str
    key_points: list[str]
    body: str
    examples: list[str]
    discussion_question: str
    visual_suggestion: str
    diagram_type: str   # process | cycle | comparison | timeline | labeled | none
    teacher_note: str


class SlidesDeck(BaseModel):
    slides: list[Slide]


def _make_agent():
    return Agent(
        role="Expert curriculum designer and classroom educator",
        goal=(
            "Create deeply detailed, classroom-ready slide content that gives teachers "
            "everything they need to deliver an engaging lesson without extra research"
        ),
        backstory=(
            "You have 20 years of experience designing lesson materials for schools. "
            "You know that shallow bullet points fail students. Every slide you write "
            "includes rich explanations, real-world examples, a visual idea, and a "
            "discussion question to drive classroom engagement."
        ),
        llm=llm,
        verbose=False,
    )


_FIELDS = (
    "  - slide_number (int)\n"
    "  - title (str): clear, specific slide title\n"
    "  - key_points (list of 4-6 str): full sentences explaining the concept, not fragments\n"
    "  - body (str): 2-3 sentence paragraph a teacher reads aloud to explain the slide\n"
    "  - examples (list of 2 str): concrete real-world examples students can relate to\n"
    "  - discussion_question (str): one open-ended question to ask the class\n"
    "  - visual_suggestion (str): specific description of a diagram or image for this slide\n"
    "  - diagram_type (str): ONLY use a diagram if it genuinely makes the concept clearer.\n"
    "      Default to 'none'. Only pick another type when a visual is essential:\n"
    "      process    = concept is a sequence of steps (e.g. how digestion works)\n"
    "      cycle      = concept is a repeating loop (e.g. water cycle, carbon cycle)\n"
    "      comparison = slide is explicitly comparing two things (e.g. plant vs animal cell)\n"
    "      timeline   = slide covers events in chronological order\n"
    "      labeled    = slide introduces a structure with named parts (e.g. parts of a cell)\n"
    "      none       = everything else — introductions, definitions, discussions, summaries\n"
    "  - teacher_note (str): 1-2 sentences of delivery advice or common misconceptions\n"
)


@llm_retry
def _run_batch(topic, grade, subject, brief, difficulty_note, start, end):
    count = end - start + 1
    agent = _make_agent()
    task = Task(
        description=(
            f"Create slides {start} through {end} (exactly {count} slides) for this lesson:\n"
            f"  Topic: {topic}\n"
            f"  Grade: {grade}\n"
            f"  Subject: {subject}\n"
            f"  Brief: {brief}\n"
            f"  Difficulty note: {difficulty_note}\n\n"
            f"For EACH slide produce ALL of these fields:\n{_FIELDS}\n"
            f"Return ONLY a valid JSON array of exactly {count} slide objects. "
            "No extra text, no markdown fences."
        ),
        expected_output=(
            f"A JSON array of {count} slide objects each with: slide_number, title, "
            "key_points, body, examples, discussion_question, visual_suggestion, "
            "diagram_type, teacher_note"
        ),
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    result = crew.kickoff()
    return parse_json(result.raw)


def run_slides_agent(
    topic: str,
    grade: str,
    subject: str,
    brief: str,
    difficulty_note: str,
) -> list:
    batch1 = _run_batch(topic, grade, subject, brief, difficulty_note, 1, 5)
    batch2 = _run_batch(topic, grade, subject, brief, difficulty_note, 6, 10)
    return batch1 + batch2
