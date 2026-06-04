from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse

from config import supabase
from export.pptx_builder import build_pptx
from export.html_builder import build_html

router = APIRouter()


@router.get("/export/pptx/{lesson_id}")
def export_pptx(lesson_id: str):
    result = supabase.table("lessons").select("pack, topic").eq("id", lesson_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Lesson not found")

    pack  = result.data["pack"]
    topic = result.data["topic"].replace(" ", "_")[:40]

    buf = build_pptx(pack)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{topic}_lesson.pptx"'},
    )


@router.get("/export/slides/{lesson_id}", response_class=HTMLResponse)
def export_slides(lesson_id: str):
    result = supabase.table("lessons").select("pack").eq("id", lesson_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Lesson not found")

    html = build_html(result.data["pack"])
    return HTMLResponse(content=html)


@router.get("/export/slides/{lesson_id}/download")
def download_slides(lesson_id: str):
    result = supabase.table("lessons").select("pack, topic").eq("id", lesson_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Lesson not found")

    pack  = result.data["pack"]
    topic = result.data["topic"].replace(" ", "_")[:40]
    html  = build_html(pack)

    return StreamingResponse(
        iter([html.encode("utf-8")]),
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{topic}_slides.html"'},
    )
