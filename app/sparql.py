# app/sparql.py

import requests

QLEVER_URL = "http://localhost:7070"


def run_sparql(query: str) -> dict:
    response = requests.post(
        QLEVER_URL,
        data={"query": query}
    )
    response.raise_for_status()
    return response.json()

