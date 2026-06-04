import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.generate import router as generate_router
from routes.refine import router as refine_router
from routes.export import router as export_router

app = FastAPI(title="ClassroomAgent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(refine_router)
app.include_router(export_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
