from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import unicodedata
from app.wikidata import search_person, get_birthday, get_students
from app.information_retrieval import (
    course_retrieval,
    objective_retrieval,
    hybrid_retrieval,
    dense_retrieval,
    build_documents,
    course_data
)
from app.llm import call_llm
from app.pipeline import answer_question

app = FastAPI()

class TextInput(BaseModel):
    text: str

def normalize_query(query: str) -> str:
    """Normalize query by removing accents and converting to lowercase.
    
    This helps with Danish queries and accent variations.
    """
    # Remove accents (e.g., ø → o, å → a, æ → ae)
    nfkd = unicodedata.normalize('NFKD', query)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower()


@app.get("/v1/health")
def health():
    doc_course_ids, _, _, _, _, objectives_text = build_documents(course_data)
    return {"status": "ok", "index_sizes": {"courses": len(doc_course_ids), "objectives": len(objectives_text)}}

@app.post("/v1/query")
def query_endpoint(text_input: TextInput):
    """
    Text-to-query endpoint:
    - takes natural language input
    - converts to SPARQL
    - queries QLever
    - returns result
    """

    try:
        result = answer_question(text_input.text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
"""
@app.post("/v1/extract-sentences")
async def extract_sentences(pdf_file: UploadFile = File(...)):
    content = await pdf_file.read()
    sentences = pdf_to_senteces(content)
    return {"sentences": sentences}
"""
"""
@app.post("/v1/extract-persons")
async def extract_persons(text_input: TextInput):
    content = text_input.text
    names = text_to_persons_llm(content)
    return {"persons": names}
"""