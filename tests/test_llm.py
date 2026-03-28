from app.llm import call_llm, extract_entities

print(call_llm("Hello"))

# tests/test_llm.py


def test_extract_entities():
    result = extract_entities("What is the width of a Yamaha P-150?")

    assert "items" in result
    assert "properties" in result