import json
from config import groq_client, llm, USE_LOCAL_LLM
from agents.utils import parse_json, llm_retry

VALID_SECTIONS = {"slides", "quiz", "assignment", "rubric", "faq"}


@llm_retry
def refine_section(
    lesson_id: str,
    section: str,
    instruction: str,
    current_content,
) -> dict | list:
    if section not in VALID_SECTIONS:
        raise ValueError(f"Invalid section '{section}'. Must be one of: {', '.join(sorted(VALID_SECTIONS))}")

    prompt = (
        f"You are editing a lesson pack section. "
        f"The section is: {section}. "
        f"Current content: {json.dumps(current_content)}. "
        f"Teacher instruction: {instruction}. "
        f"Return ONLY the updated {section} in the exact same JSON format. No extra text."
    )

    if USE_LOCAL_LLM:
        raw = llm.call([{"role": "user", "content": prompt}])
        return parse_json(raw)

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return parse_json(response.choices[0].message.content)
