import requests
from lxml import etree
from nltk.tokenize import sent_tokenize
import os

GROBID_URL = os.getenv("GROBID_URL", "http://localhost:8070")

def pdf_to_senteces(content):
    response = requests.post(
        f"{GROBID_URL}/api/processFulltextDocument",
        files={"input": ("file.pdf", content, "application/pdf")}
    )

    xml = response.text

    root = etree.fromstring(xml.encode()) # string in memory

    ns = {"tei": "http://www.tei-c.org/ns/1.0"} # XPath-based extraction of the sentences

    paragraphs = root.xpath("//tei:p", namespaces=ns)

    text_parts = [
    etree.tostring(p, method="text", encoding="unicode").strip()
    for p in paragraphs
    ]

    full_text = " ".join(text_parts)

    sentences = sent_tokenize(full_text)

    return sentences