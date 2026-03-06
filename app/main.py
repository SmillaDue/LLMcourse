from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from app.wikidata import search_person, get_birthday, get_students
from app.information_retrieval import course_retrieval, objective_retrieval, build_documents, course_data


app = FastAPI()



class TextInput(BaseModel):
    text: str


"""
class PersonRequest(BaseModel):
    person: str
    context: str | None = None

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


@app.get("/v1/search")
def search_courses(query: str, top_k: int = 5):
    results = course_retrieval(course_data, query)
    return {"query": query, "results": results[:top_k]}


@app.get("/v1/objectives/search")
def search_objectives(query: str, top_k: int = 5):
    results = objective_retrieval(course_data, query)
    return {"query": query, "results": results[:top_k]}


@app.get("/v1/courses/{course_id}/similar")
def similar_courses(course_id: str, top_k: int = 5):
    # Find the course and use its text as the query
    course = next((c for c in course_data if c["course_code"] == course_id), None)
    if course is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
    query = course["title"] + "\n" + "\n".join(course["learning_objectives"])
    results = course_retrieval(course_data, query)
    # Exclude the query course itself from results
    results = [r for r in results if r["course_id"] != course_id]
    return {"query_course_id": course_id, "results": results[:top_k]}


@app.get("/v1/health")
def health():
    doc_course_ids, _, _, _, _, objectives_text = build_documents(course_data)
    return {"status": "ok", "index_sizes": {"courses": len(doc_course_ids), "objectives": len(objectives_text)}}
