from json_repair import repair_json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception


def parse_json(raw: str):
    return repair_json(raw, return_objects=True)


def _is_retryable(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return any(k in msg for k in ("rate limit", "ratelimit", "429", "timeout", "connection"))


llm_retry = retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    stop=stop_after_attempt(4),
    reraise=True,
)
