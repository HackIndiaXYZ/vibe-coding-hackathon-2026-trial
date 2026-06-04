import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.orchestrator import run_orchestrator
from agents.difficulty import enrich_briefs
from agents.slides import run_slides_agent
from agents.quiz import run_quiz_agent
from agents.assignment import run_assignment_agent
from agents.rubric import run_rubric_agent
from agents.faq import run_faq_agent
from agents.assembler import assemble_lesson

router = APIRouter()

_executor = ThreadPoolExecutor()


class GenerateRequest(BaseModel):
    topic: str
    grade: str
    subject: str
    struggle_areas: list[str] = []


@router.post("/generate")
async def generate(body: GenerateRequest):
    topic = body.topic
    grade = body.grade
    subject = body.subject
    struggle_areas = body.struggle_areas

    loop = asyncio.get_event_loop()

    def run_sync(fn, *args):
        return fn(*args)

    try:
        orchestrator_output = await loop.run_in_executor(
            _executor, run_sync, run_orchestrator, topic, grade, subject, struggle_areas
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator failed: {e}")

    enriched = enrich_briefs(orchestrator_output, struggle_areas, grade)

    difficulty_note = enriched["difficulty_note"]

    agent_args = {
        "slides":     (run_slides_agent,     topic, grade, subject, enriched["slides_brief"],     difficulty_note),
        "quiz":       (run_quiz_agent,        topic, grade, subject, enriched["quiz_brief"],       difficulty_note),
        "assignment": (run_assignment_agent,  topic, grade, subject, enriched["assignment_brief"], difficulty_note),
        "rubric":     (run_rubric_agent,      topic, grade, subject, enriched["rubric_brief"],     difficulty_note),
        "faq":        (run_faq_agent,         topic, grade, subject, enriched["faq_brief"],        difficulty_note),
    }

    outputs = {}
    for name, (fn, *args) in agent_args.items():
        try:
            outputs[name] = await loop.run_in_executor(_executor, run_sync, fn, *args)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{name} agent failed: {e}")

    try:
        lesson = assemble_lesson(
            topic, grade, subject,
            slides=outputs["slides"],
            quiz=outputs["quiz"],
            assignment=outputs["assignment"],
            rubric=outputs["rubric"],
            faq=outputs["faq"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assembly/save failed: {e}")

    return lesson
