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

app = FastAPI()


def normalize_query(query: str) -> str:
    """Normalize query by removing accents and converting to lowercase.
    
    This helps with Danish queries and accent variations.
    """
    # Remove accents (e.g., ø → o, å → a, æ → ae)
    nfkd = unicodedata.normalize('NFKD', query)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower()


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
def search_courses(query: str, top_k: int = 5, mode: str = "sparse"):
    if mode == "sparse":
        results = course_retrieval(course_data, query, top_k=top_k)
    elif mode == "dense":
        results = dense_retrieval(course_data, query, top_k=top_k)
    elif mode == "hybrid":
        results = hybrid_retrieval(course_data, query, top_k=top_k)
    else:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    return {"query": query, "results": results}

@app.get("/v1/ask")
def ask(query: str, top_k: int = 5, mode: str = "hybrid", alpha: float = 0.6):
    # 1. Retrieve documents
    if mode == "sparse":
        results = course_retrieval(course_data, query, top_k=top_k)
    elif mode == "dense":
        results = dense_retrieval(course_data, query, top_k=top_k)
    elif mode == "hybrid":
        results = hybrid_retrieval(course_data, query, alpha=alpha, top_k=top_k)
    else:
        raise HTTPException(status_code=400, detail="Invalid mode")

    # 2. Build context
    course_lookup = {c["course_code"]: c for c in course_data}

    context = ""
    for r in results:
        course = course_lookup[r["course_id"]]

        content = course.get("content", "")
        content = content[:1000]  # Include more content
        
        context += f"""
Course: {course['title']}
Code: {course['course_code']}
Department: {course['fields'].get('Department', 'Unknown')}
Teacher: {course['fields'].get('Responsible', 'Unknown')}
ECTS: {course['fields'].get('Point( ECTS )', 'Unknown')}
Language: {course['fields'].get('Language of instruction', 'Unknown')}
Learning Objectives: {'; '.join(course['learning_objectives'])}
Content: {content}
---
"""
    
    context = context[:5000]  # More generous context limit

    # 3. Build prompt
    prompt = f"""You are a helpful assistant for DTU course information.

Answer the question based on the provided context.
If the answer is not found in the context, say "I don't know".
Be concise and precise.

Question: {query}

Context:
{context}

Answer:"""

    # 4. Call LLM
    answer = call_llm(prompt)

    return {
        "query": query,
        "answer": answer,
        "retrieved_courses": results
    }

@app.get("/v1/objectives/search")
def search_objectives(query: str, top_k: int = 5):
    results = objective_retrieval(course_data, query, top_k=top_k)
    return {"query": query, "results": results}


@app.get("/v1/courses/{course_id}/similar")
def similar_courses(course_id: str, top_k: int = 5):
    # Find the course and use its text as the query
    course = next((c for c in course_data if c["course_code"] == course_id), None)
    if course is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
    query = course["title"] + "\n" + "\n".join(course["learning_objectives"])
    results = course_retrieval(course_data, query, top_k=top_k)
    # Exclude the query course itself from results
    results = [r for r in results if r["course_id"] != course_id]
    return {"query_course_id": course_id, "results": results}


@app.get("/v1/health")
def health():
    doc_course_ids, _, _, _, _, objectives_text = build_documents(course_data)
    return {"status": "ok", "index_sizes": {"courses": len(doc_course_ids), "objectives": len(objectives_text)}}
