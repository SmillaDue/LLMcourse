from fastapi import FastAPI
from pydantic import BaseModel

from app.sentiment import sentiment

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/v1/sentiment")
def analyze_sentiment(input: TextInput):
    result = sentiment(input.text)
    return {"sentiment": result}