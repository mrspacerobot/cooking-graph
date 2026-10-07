"""Ask Wikidata's query service for food items by English label, with their labels in other languages.

This is the only part of the importer that reaches the network. It asks politely: one
identifying User-Agent, small batches, a pause between them, and a wait when told to.
Only items that are a food or a food ingredient are returned.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "cooking-graph-importer/0.1 (a private knowledge graph; contact the repository owner)"
FOOD_CLASSES = ("wd:Q2095", "wd:Q25403900")  # food, food ingredient: their labels were fetched and read, not remembered
BATCH = 25
PAUSE = 1.5


def variants(label):
    """A label as it is written here and in lower case, which is how Wikidata writes most common nouns."""
    return [label] if label == label.lower() else [label, label.lower()]


def quote(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def query(labels, languages):
    values = " ".join(quote(label) + "@en" for label in labels)
    wanted = ", ".join(quote(language) for language in languages)
    return """SELECT ?item ?enLabel ?lang ?name WHERE {
  VALUES ?enLabel { %s }
  VALUES ?class { %s }
  ?item rdfs:label ?enLabel .
  ?item wdt:P31/wdt:P279* ?class .
  OPTIONAL { ?item rdfs:label ?name . BIND(LANG(?name) AS ?lang) FILTER(?lang IN (%s)) }
}""" % (values, " ".join(FOOD_CLASSES), wanted)


def entities(answer):
    """One entity per item from a SPARQL answer. Every item the query returns is a food."""
    found = {}
    for row in answer["results"]["bindings"]:
        qid = row["item"]["value"].rsplit("/", 1)[-1]
        one = found.setdefault(qid, {"label": row["enLabel"]["value"], "qid": qid, "food": True, "labels": {}})
        if "lang" in row and "name" in row:
            one["labels"][row["lang"]["value"]] = row["name"]["value"]
    return list(found.values())


def ask(text, tries=4):
    body = urllib.parse.urlencode({"query": text, "format": "json"}).encode("utf-8")
    request = urllib.request.Request(ENDPOINT, data=body, headers={
        "User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
            time.sleep(int(error.headers.get("Retry-After", 5 * (attempt + 1))))
    raise RuntimeError("unreachable")


def fetch(labels, languages, progress=None):
    """Entities for the labels, a batch at a time."""
    wanted = sorted({variant for label in labels for variant in variants(label)})
    found = {}
    for start in range(0, len(wanted), BATCH):
        batch = wanted[start:start + BATCH]
        for one in entities(ask(query(batch, languages))):
            found[(one["qid"], one["label"])] = one
        if progress:
            progress(min(start + BATCH, len(wanted)), len(wanted))
        time.sleep(PAUSE)
    return list(found.values())
