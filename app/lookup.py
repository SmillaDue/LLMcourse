# app/lookup.py

from app.sparql import run_sparql


def lookup_property(label: str) -> str:
    """
    Given a human-readable property name (e.g., "width"),
    find the corresponding property ID (PID) in the knowledge graph.

    This implements the "property lookup" step from the assignment:
    natural language → graph identifier (kbt:P...)

    Example:
        input:  "width"
        output: "http://.../P2"
    """

    # ------------------------------------------------------------------
    # 1. Build SPARQL query
    # ------------------------------------------------------------------
    # We follow the exact template from the assignment.
    #
    # The query searches for a property where:
    #   - its label OR alternative label matches the given text
    #
    # rdfs:label       = main name (e.g., "width")
    # skos:altLabel    = alternative names / synonyms
    #
    # The "|" means OR in SPARQL.
    #
    # "@en" means: only match English labels
    #
    # <http://wikiba.se/ontology#directClaim> links the property item
    # to the actual property ID (P-ID) we want to use in queries.

    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?property WHERE {{
    ?property_item rdfs:label | skos:altLabel ?label_value ;
                    <http://wikiba.se/ontology#directClaim> ?property .

    FILTER(
        (?label_value = "{label}"@en) ||
        (?label_value = "{label}"@da)
    )
    }}
    """

    # ------------------------------------------------------------------
    # 2. Send query to QLever
    # ------------------------------------------------------------------
    # This uses your previously implemented function.
    # It sends the SPARQL query to:
    #     http://localhost:7070
    #
    # and returns a JSON response.

    result = run_sparql(query)

    # ------------------------------------------------------------------
    # 3. Extract results from JSON
    # ------------------------------------------------------------------
    # SPARQL results come in a standard format:
    #
    # {
    #   "results": {
    #       "bindings": [ ... ]
    #   }
    # }
    #
    # "bindings" is a list of matches

    bindings = result["results"]["bindings"]

    # ------------------------------------------------------------------
    # 4. Handle case where nothing is found
    # ------------------------------------------------------------------
    # If no property matches the label, we raise an error.
    # This is important for debugging and later system behavior.

    if not bindings:
        raise ValueError(f"No property found for label: {label}")

    # ------------------------------------------------------------------
    # 5. Extract the property ID (PID)
    # ------------------------------------------------------------------
    # Each binding looks like:
    #
    # {
    #   "property": {
    #       "type": "uri",
    #       "value": "http://.../P2"
    #   }
    # }
    #
    # We take the FIRST match (baseline approach)

    property_uri = bindings[0]["property"]["value"]

    # ------------------------------------------------------------------
    # 6. Return the property ID
    # ------------------------------------------------------------------
    return property_uri


from app.sparql import run_sparql


def lookup_item(label: str) -> str:
    """
    Given a human-readable item name (e.g., "Yamaha P-150"),
    find the corresponding entity ID (QID) in the knowledge graph.

    This implements:
        natural language → graph entity (kb:Q...)

    Example:
        input:  "Yamaha P-150"
        output: "http://.../Q1"
    """

    # ------------------------------------------------------------------
    # 1. Build SPARQL query
    # ------------------------------------------------------------------
    # We search for an entity (?item) whose:
    #   - label OR alternative label matches the given text
    #
    # Same idea as lookup_property, but simpler:
    #   - we directly return ?item
    #   - no need for directClaim

    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?item WHERE {{
    ?item rdfs:label | skos:altLabel ?label_value .

    FILTER(
        (LCASE(STR(?label_value)) = LCASE("{label}") && LANG(?label_value) = "en") ||
        (LCASE(STR(?label_value)) = LCASE("{label}") && LANG(?label_value) = "da")
    )
    }}
    """

    # ------------------------------------------------------------------
    # 2. Run query against QLever
    # ------------------------------------------------------------------
    result = run_sparql(query)

    # ------------------------------------------------------------------
    # 3. Extract results
    # ------------------------------------------------------------------
    bindings = result["results"]["bindings"]

    # ------------------------------------------------------------------
    # 4. Handle no matches
    # ------------------------------------------------------------------
    if not bindings:
        raise ValueError(f"No item found for label: {label}")

    # ------------------------------------------------------------------
    # 5. Return the first matching item (QID URI)
    # ------------------------------------------------------------------
    item_uri = bindings[0]["item"]["value"]

    return item_uri