from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from app.wikidata import search_person, get_birthday, get_students



app = FastAPI()

class PersonRequest(BaseModel):
    person: str
    context: str | None = None

class TextInput(BaseModel):
    text: str



@app.post("/v1/birthday")
async def birtday(request: PersonRequest):

    qid = search_person(request.person)
    birthday = get_birthday(qid)

    return {
        "person": request.person,
        "qid": qid,
        "birtday": birthday
    }


@app.post("/v1/students")
def students(request: PersonRequest):

    qid = search_person(request.person)
    students = get_students(qid)

    return {
        "person": request.person,
        "qid": qid,
        "students": students
    }


@app.post("/v1/all")
def all_info(request: PersonRequest):
    qid = search_person(request.person)
    birthday = get_birthday(qid)
    students = get_students(qid)

    return {
        "person": request.person,
        "qid": qid,
        "birthday": birthday,
        "students": students
    }


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

