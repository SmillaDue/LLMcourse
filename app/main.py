from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from app.pdf import pdf_to_senteces

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/v1/extract-sentences")
async def extract_sentences(pdf_file: UploadFile = File(...)):
    content = await pdf_file.read()
    sentences = pdf_to_senteces(content)
    return {"sentences": sentences}

