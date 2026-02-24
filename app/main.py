from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from app.names import text_to_persons_llm

app = FastAPI()

class TextInput(BaseModel):
    text: str

"""
@app.post("/v1/extract-sentences")
async def extract_sentences(pdf_file: UploadFile = File(...)):
    content = await pdf_file.read()
    sentences = pdf_to_senteces(content)
    return {"sentences": sentences}
"""

@app.post("/v1/extract-persons")
async def extract_persons(text_input: TextInput):
    content = text_input.text
    names = text_to_persons_llm(content)
    return {"persons": names}
