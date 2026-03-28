import os
from dotenv import load_dotenv
import dspy
import json
import re

load_dotenv(os.path.expanduser("~/.env"))

api_key = os.getenv("CAMPUSAI_API_KEY")
model = "openai/" + os.getenv("CAMPUSAI_MODEL")   # e.g. "Gemma3"
api_url = os.getenv("CAMPUSAI_API_URL")

lm = dspy.LM(
    model=model,
    api_key=api_key,
    api_base=api_url
)

def call_llm(prompt: str) -> str:
    response = lm(prompt)
    
    # If response is a list, extract first element
    if isinstance(response, list):
        return response[0]
    
    return str(response)


def extract_entities(text: str) -> dict:
    """
    Use the LLM (via DSPy) to extract:
    - items
    - properties

    from a natural language query.
    """

    # ------------------------------------------------------------------
    # 1. Prompt (VERY IMPORTANT)
    # ------------------------------------------------------------------
    prompt = f"""
    Extract the item and property from the following query.

    IMPORTANT:
    - Normalize properties to canonical forms used in a keyboard database.
    - Examples:
        "number of keys" → "keys"
        "how many keys" → "keys"
        "wide" → "width"
        "højde" → "height"
        "bredde" → "width"

    Return ONLY valid JSON with this format:
    {{
    "items": ["..."],
    "properties": ["..."]
    }}

    Query:
    "{text}"

    Example:
    Input: "What is the width of a Yamaha P-150?"
    Output:
    {{"items": ["Yamaha P-150"], "properties": ["width"]}}
    """

    # ------------------------------------------------------------------
    # 2. Call your existing LLM wrapper
    # ------------------------------------------------------------------
    response = call_llm(prompt)

    # ------------------------------------------------------------------
    # Extract JSON from LLM output (handles ```json ... ```)
    # ------------------------------------------------------------------
    match = re.search(r"\{.*\}", response, re.DOTALL)

    if not match:
        raise ValueError(f"No JSON found in LLM output: {response}")

    json_str = match.group()

    return json.loads(json_str)