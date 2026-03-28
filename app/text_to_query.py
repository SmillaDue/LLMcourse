# app/text_to_query.py

from app.lookup import lookup_item, lookup_property
from app.llm import extract_entities


def text_to_query(text: str) -> str:
    """
    Convert a natural language question into a SPARQL query.

    Baseline version:
    - assumes fixed structure
    - hardcodes property extraction (for now)
    """

    # ------------------------------------------------------------------
    # 1. entity extraction 
    # ------------------------------------------------------------------

    entities = extract_entities(text)
    item_label = entities["items"][0]
    property_label = entities["properties"][0]

    # ------------------------------------------------------------------
    # 2. Lookup graph IDs
    # ------------------------------------------------------------------
    item = lookup_item(item_label)
    prop = lookup_property(property_label)

    # ------------------------------------------------------------------
    # 3. Build SPARQL query
    # ------------------------------------------------------------------
    sparql = f"""
    SELECT ?value WHERE {{
      <{item}> <{prop}> ?value .
    }}
    """

    return sparql