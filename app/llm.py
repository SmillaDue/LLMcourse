import os
from dotenv import load_dotenv
import dspy

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