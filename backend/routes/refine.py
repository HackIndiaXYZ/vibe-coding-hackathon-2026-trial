from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.refiner import refine_section, VALID_SECTIONS
from config import supabase

router = APIRouter()


class RefineRequest(BaseModel):
    lesson_id: str
    section: str
    instruction: str


@router.post("/refine")
def refine(body: RefineRequest):
    lesson_id   = body.lesson_id
    section     = body.section
    instruction = body.instruction

    if section not in VALID_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section '{section}'. Must be one of: {', '.join(sorted(VALID_SECTIONS))}",
        )

    try:
        response = supabase.table("lessons").select("pack").eq("id", lesson_id).single().execute()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Lesson not found: {e}")

    pack = response.data.get("pack", {})
    current_content = pack.get(section)
    if current_content is None:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found in lesson")

    try:
        updated_content = refine_section(lesson_id, section, instruction, current_content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {e}")

    pack[section] = updated_content
    try:
        supabase.table("lessons").update({"pack": pack}).eq("id", lesson_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save updated section: {e}")

    return {
        "lesson_id": lesson_id,
        "section": section,
        "updated_content": updated_content,
    }
