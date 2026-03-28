from app.pipeline import answer_question

def test_full_pipeline():
    result = answer_question("What is the width of a Yamaha P-150?")

    # Check structure
    assert "results" in result
    assert "sparql" in result

    # Check SPARQL looks correct
    assert "SELECT" in result["sparql"]

    # Check results are not empty
    bindings = result["results"]["results"]["bindings"]
    assert len(bindings) > 0


def test_full_pipeline_expected_width():
    result = answer_question("What is the width of a Yamaha P-150?")

    bindings = result["results"]["results"]["bindings"]

    assert len(bindings) > 0

    value = float(bindings[0]["value"]["value"])

    # You can adjust this if dataset differs
    assert value > 1000
    assert value < 2000