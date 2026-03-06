# Imports
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load course json from data directory
with open("./data/dtu_courses.jsonl", "r") as f:
    course_data = [json.loads(line) for line in f]

def build_documents(course_data):
    """Build documents for information retrieval from course data.

    Args:
        course_data: List of course dictionaries.

    Returns:
        Tuple of lists: (doc_course_ids, doc_titles, doc_text, objectives_course_ids, objectives_titles, objectives_text)
    """

    doc_course_ids = []
    doc_titles = []
    doc_text = []

    objectives_course_ids = []
    objectives_titles = []
    objectives_text = []

    for course in course_data:
        # Extract course information
        title = course["title"]
        course_id = course["course_code"]
        learning_objectives = course["learning_objectives"]

        # Append to course document lists
        doc_course_ids.append(course_id)
        doc_titles.append(title)
        doc_text.append(title + "\n" + "\n".join(learning_objectives))

        # Append to learning objectives document lists
        for objective in learning_objectives:
            objectives_course_ids.append(course_id)
            objectives_titles.append(title)
            objectives_text.append(title + "\n" + objective)

    return doc_course_ids, doc_titles, doc_text, objectives_course_ids, objectives_titles, objectives_text


def course_retrieval(course_data, query):
    """Perform course retrieval using cosine similarity.

    Args:
        course_data: List of course dictionaries.
        query: Query string.

    """

    doc_course_ids, doc_titles, doc_text, objectives_course_ids, objectives_titles, objectives_text = build_documents(course_data)

    # TF-IDF: weights words by how frequent they are in a doc vs. how rare they are across all docs
    # ngram_range=(1,2) includes both single words and two-word phrases (e.g. "machine learning")
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1,2))

    # Learn vocabulary + IDF weights from all docs, then convert each doc to a TF-IDF vector
    doc_matrix = vectorizer.fit_transform(doc_text)

    # Convert query using the same vocabulary (no refitting — must stay in the same vector space)
    query_vec = vectorizer.transform([query])

    # Cosine similarity: 1.0 = identical direction, 0.0 = no shared terms
    scores = cosine_similarity(query_vec, doc_matrix)[0]

    # Sort scores descending, take top 5 indices
    top_indices = scores.argsort()[::-1][:5]

    return [{
        "course_id": doc_course_ids[i],
        "title": doc_titles[i],
        "score": float(scores[i])
    } for i in top_indices]


def objective_retrieval(course_data, query):
    """Perform learning objective retrieval using cosine similarity.

    Args:
        course_data: List of course dictionaries.
        query: Query string.

    """

    doc_course_ids, doc_titles, doc_text, objectives_course_ids, objectives_titles, objectives_text = build_documents(course_data)

    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1,2))
    doc_matrix = vectorizer.fit_transform(objectives_text)
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, doc_matrix)[0]
    top_indices = scores.argsort()[::-1][:5]

    return [{
        "course_id": objectives_course_ids[i],
        "title": objectives_titles[i],
        "objective": objectives_text[i].split("\n", 1)[1],  # Remove title from objective text
        "score": float(scores[i])
    } for i in top_indices]