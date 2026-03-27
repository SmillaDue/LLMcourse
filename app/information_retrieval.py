# Imports
import json
import unicodedata
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def normalize_text(text: str) -> str:
    """Remove accents and convert to lowercase for matching."""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower()

# Load course json from data directory
with open("./data/dtu_courses.jsonl", "r") as f:
    course_data = [json.loads(line) for line in f]

# Initialize sentence transformer for embedding generation
dense_model = SentenceTransformer('all-MiniLM-L6-v2')

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
        fields = course.get("fields", {})
        
        # Extract relevant fields for indexing
        responsible = fields.get("Responsible", "")
        content = course.get("content", "")

        # Append to course document lists
        # Include title, objectives, teacher, and content for better retrieval
        # Normalize text to handle accents (ø→o, å→a, etc.)
        normalized_text = normalize_text(
            title + "\n" + 
            responsible + "\n" +
            "\n".join(learning_objectives) + "\n" +
            content[:500]  # Include preview of content
        )
        
        doc_course_ids.append(course_id)
        doc_titles.append(title)
        doc_text.append(normalized_text)

        # Append to learning objectives document lists
        for objective in learning_objectives:
            objectives_course_ids.append(course_id)
            objectives_titles.append(title)
            objectives_text.append(title + "\n" + objective)

    return doc_course_ids, doc_titles, doc_text, objectives_course_ids, objectives_titles, objectives_text


def course_retrieval(course_data, query, return_scores=False, top_k=5):
    """Perform course retrieval using cosine similarity.

    Args:
        course_data: List of course dictionaries.
        query: Query string.
        return_scores: Whether to return similarity scores.

    """

    doc_course_ids, doc_titles, doc_text, objectives_course_ids, objectives_titles, objectives_text = build_documents(course_data)

    # Normalize query to match normalized documents
    normalized_query = normalize_text(query)

    # TF-IDF: weights words by how frequent they are in a doc vs. how rare they are across all docs
    # ngram_range=(1,2) includes both single words and two-word phrases (e.g. "machine learning")
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1,2))

    # Learn vocabulary + IDF weights from all docs, then convert each doc to a TF-IDF vector
    doc_matrix = vectorizer.fit_transform(doc_text)

    # Convert query using the same vocabulary (no refitting — must stay in the same vector space)
    query_vec = vectorizer.transform([normalized_query])

    # Cosine similarity: 1.0 = identical direction, 0.0 = no shared terms
    scores = cosine_similarity(query_vec, doc_matrix)[0]

    if return_scores:
        return doc_course_ids, doc_titles, scores
    
    # Sort scores descending
    top_indices = scores.argsort()[::-1][:top_k]

    return [{
        "course_id": doc_course_ids[i],
        "title": doc_titles[i],
        "score": float(scores[i])
    } for i in top_indices]


def objective_retrieval(course_data, query, top_k=5):
    """Perform learning objective retrieval using cosine similarity.

    Args:
        course_data: List of course dictionaries.
        query: Query string.
        top_k: Number of top results to return.

    """

    doc_course_ids, doc_titles, doc_text, objectives_course_ids, objectives_titles, objectives_text = build_documents(course_data)

    # Normalize query
    normalized_query = normalize_text(query)

    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1,2))
    doc_matrix = vectorizer.fit_transform(objectives_text)
    query_vec = vectorizer.transform([normalized_query])
    scores = cosine_similarity(query_vec, doc_matrix)[0]
    top_indices = scores.argsort()[::-1][:top_k]

    return [{
        "course_id": objectives_course_ids[i],
        "title": objectives_titles[i],
        "objective": objectives_text[i].split("\n", 1)[1],  # Remove title from objective text
        "score": float(scores[i])
    } for i in top_indices]

def build_dense_matrix(doc_text):
    """Build dense embedding matrix for documents using sentence transformer.

    Args:
        doc_text: List of document texts.   
    Returns:        Numpy array of shape (num_docs, embedding_dim) with normalized embeddings.
    """
    return dense_model.encode(doc_text, normalize_embeddings=True)

def dense_retrieval(course_data, query, top_k=5):
    doc_course_ids, doc_titles, doc_text, _, _, _ = build_documents(course_data)

    # Normalize query for consistency
    normalized_query = normalize_text(query)

    doc_embeddings = build_dense_matrix(doc_text)
    query_embedding = dense_model.encode([normalized_query], normalize_embeddings=True)

    scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_indices = scores.argsort()[::-1][:top_k]

    return [{
        "course_id": doc_course_ids[i],
        "title": doc_titles[i],
        "score": float(scores[i])
    } for i in top_indices]

import numpy as np

def normalize(scores):
    if scores.max() == scores.min():
        return scores
    return (scores - scores.min()) / (scores.max() - scores.min())

def hybrid_retrieval(course_data, query, alpha=0.6, top_k=5):
    # Get documents
    doc_ids, titles, doc_text, _, _, _ = build_documents(course_data)
    
    # Normalize query once
    normalized_query = normalize_text(query)
    
    # Sparse
    _, _, sparse = course_retrieval(course_data, query, return_scores=True)

    # Dense
    dense_embeddings = dense_model.encode(doc_text, normalize_embeddings=True)
    query_embedding = dense_model.encode([normalized_query], normalize_embeddings=True)
    dense = cosine_similarity(query_embedding, dense_embeddings)[0]

    # Normalize
    sparse = normalize(sparse)
    dense = normalize(dense)

    # Combine
    combined_scores = alpha * dense + (1 - alpha) * sparse

    top_indices = combined_scores.argsort()[::-1][:top_k]

    return [{
        "course_id": doc_ids[i],
        "title": titles[i],
        "score": float(combined_scores[i])
    } for i in top_indices]