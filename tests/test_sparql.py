# tests/test_sparql.py

from app.sparql import run_sparql


def test_basic_query():
    query = """
    SELECT * WHERE {
        ?s ?p ?o
    } LIMIT 1
    """

    result = run_sparql(query)

    assert "results" in result