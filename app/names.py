import spacy
import os
import requests
import json
import re

# Get configuration from environment variables
api_key = os.getenv("CAMPUSAI_API_KEY")  # Your CampusAI API key
model = os.getenv("CAMPUSAI_MODEL")  # Which model to use (e.g., gpt-4o-mini)
base_url = os.getenv("CAMPUSAI_API_URL")  # CampusAI API base URL


def text_to_persons_llm(text):
    """Extract person names from text using CampusAI LLM API.
    
    Args:
        text: The text to extract person names from
        
    Returns:
        List of person names as strings
    """
    # Set up authorization header with API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Prepare the request to the LLM
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system", 
                "content": "Extract all person names from the text and return them as a JSON array of strings. Return only the JSON array, nothing else."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0  # Low temperature for consistent results
    }

    # Send request to CampusAI API
    response = requests.post(base_url + "/chat/completions", json=payload, headers=headers)

    # Check if request was successful
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    # Parse the JSON response
    result = response.json()
    
    # Get the text content from the LLM's response
    content = result["choices"][0]["message"]["content"]

    # Clean up markdown code blocks if present (```python, ```json, etc.)
    content = content.strip()
    content = re.sub(r'^```(?:python|json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    content = content.strip()
    
    # Parse the JSON array string into a Python list
    names = json.loads(content)
    
    return names



def text_to_persons_spacy(text):
    """Extract person names from text using spaCy NLP library.
    
    Args:
        text: The text to extract person names from
        
    Returns:
        List of person names as strings
    """
    # Load spaCy's transformer-based English model
    nlp = spacy.load("en_core_web_trf")
    
    # Process the text through the NLP pipeline
    doc = nlp(text)

    names = []

    # Loop through all entities found in the text
    for ent in doc.ents :
        # Only keep entities labeled as "PERSON"
        if ent.label_ == "PERSON":
            names.append(ent.text)
    
    return names