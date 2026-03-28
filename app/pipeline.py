from app.text_to_query import text_to_query
from app.sparql import run_sparql


def answer_question(text: str) -> dict:
    """
    Full pipeline:
    Natural language → SPARQL → execution → result

    This is the "end-to-end system" of the assignment.
    """

    # Step 1: Convert text → SPARQL query
    sparql = text_to_query(text)

    # Step 2: Execute SPARQL query against QLever
    results = run_sparql(sparql)

    # Step 3: Return structured response
    return {
        "query": text,
        "sparql": sparql,
        "results": results
    }