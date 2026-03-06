import spacy
import os
import requests
import json
import re
import httpx
from fastapi import HTTPException

# Get configuration from environment variables
api_key = os.getenv("CAMPUSAI_API_KEY")  # Your CampusAI API key
model = os.getenv("CAMPUSAI_MODEL")  # Which model to use (e.g., gpt-4o-mini)
base_url = os.getenv("CAMPUSAI_API_URL")  # CampusAI API base URL

# get global variables
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

HEADERS = {
    "User-Agent": "s204153@dtu.dk",  
    "Accept": "application/sparql-results+json"
}

def search_person(person_name: str) -> str:
    params = {
        "action": "wbsearchentities",
        "search": person_name,   # the query string
        "language": "en",         # specifies search language as English
        "type": "item",
        "format": "json",         # output format
        "limit": 5                # limit the number of search results returned
    }

    response = httpx.get(
        WIKIDATA_API,
        params=params,
        headers=HEADERS
    )

    data = response.json()
    try:
        return data["search"][0]["id"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=404, detail="Person not found")


def get_birthday(qid: str) -> str:
    query = f""" 
    SELECT ?birthday WHERE {{
        wd:{qid} wdt:P569 ?birthday .
    }}
    """
    params = {
        "query": query,
        "format": "json"
    }

    response = httpx.get(
        SPARQL_ENDPOINT,
        params=params,
        headers=HEADERS
    )

    data = response.json()

    try:
        raw_value = data["results"]["bindings"][0]["birthday"]["value"]
        birthday = raw_value.split("T")[0]
        return birthday
    except (KeyError, IndexError):
        raise HTTPException(status_code=404, detail="Birthday not found")


def get_students(qid: str) -> list[dict]:
    query = f""" 
    SELECT ?student ?studentLabel WHERE {{
        wd:{qid} wdt:P802 ?student .
        SERVICE wikibase:label {{bd:serviceParam wikibase:language "en".}}
    }}
    """
    params = {
        "query": query,
        "format": "json"
    }

    response = httpx.get(
        SPARQL_ENDPOINT,
        params=params,
        headers=HEADERS
    )

    data = response.json()

    students = []

    bindings = data["results"]["bindings"]

    for entry in bindings:
        uri = entry["student"]["value"]
        name = entry["studentLabel"]["value"]
        qid = uri.split("/")[-1]
        students.append({"label": name, "qid": qid})

    return students
   