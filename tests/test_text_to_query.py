# tests/test_text_to_query.py

from app.text_to_query import text_to_query


def test_text_to_query():
    query = text_to_query("What is the width of a Yamaha P-150?")

    assert "SELECT" in query
    assert "WHERE" in query