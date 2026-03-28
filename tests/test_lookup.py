# tests/test_lookup.py

from app.lookup import lookup_property, lookup_item


def test_lookup_width():
    prop = lookup_property("width")

    assert prop.startswith("http")


def test_lookup_item():
    item = lookup_item("Yamaha P-150")

    assert item.startswith("http")