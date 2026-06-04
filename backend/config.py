import os
import crewai.llms.cache as _cache
_cache.mark_cache_breakpoint = lambda msg: msg  # Groq doesn't support cache_breakpoint

from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv
from crewai.llm import LLM

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"

if USE_LOCAL_LLM:
    llm = LLM(
        model="ollama/qwen2.5:7b",
        base_url="http://localhost:11434",
    )
else:
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
    )

groq_client = Groq(api_key=GROQ_API_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
