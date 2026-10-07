"""Build the graph's internal review page from the current checkout and open it."""

import argparse
import json
import subprocess
import sys
import webbrowser
from collections import Counter
from pathlib import Path

from tools import check, names, queries, reading

LABELS = {
    "makes": "makes", "ingredients": "uses ingredient", "options": "part option",
    "technique": "uses technique", "teaches": "teaches", "groups": "belongs to group",
    "works_on": "works on", "with": "uses with", "equipment": "needs equipment",
    "forms": "starting form", "belongs_to": "belongs to cuisine",
    "stands_in_for": "stand-in (context)", "contains": "contains (safety record)",
    "free_of": "free of (safety record)", "is_a": "is a", "part_of": "part of",
    "in_pantry_of": "pantry of",
}


def object_fields(rule, model):
    if rule["is"] == "shape":
        return object_fields(model["shapes"][rule["name"]], model)
    if rule["is"] == "link":
        return dict({"thing": {"is": "ref"}}, **rule.get("with", {}))
    return rule.get("fields", {})


def references(value, rule, model, path=()):
    """Follow only references declared by the schema, never words that resemble ids."""
    if value is None:
        return
    if rule["is"] == "ref":
        yield path, value
    elif rule["is"] == "list":
        for item in value:
            yield from references(item, rule["of"], model, path)
    else:
        for field, nested in object_fields(rule, model).items():
            yield from references(value[field], nested, model, path + (field,))


def edges_for(thing, model):
    fields = model["kinds"][thing.kind]["fields"]
    for path, target in references(thing.data, {"is": "object", "fields": fields}, model):
        relation = path[-1]
        if relation in ("thing", "fact"):
            relation = path[-2]
        if relation not in ("when", "not_when"):
            yield {"source": thing.data["id"], "target": target, "relation": relation,
                   "label": LABELS.get(relation, relation.replace("_", " "))}


def node_for(thing):
    data = thing.data
    fallback = data.get("title", data["id"].split("/")[1].replace("-", " ").title())
    name = data.get("names", {}).get("en", fallback)
    searchable = [data["id"], name] + names.all_names(data)
    return {"id": data["id"], "kind": thing.kind, "name": name, "path": thing.path,
            "search": " ".join(searchable).lower(), "raw": data}


def payload(things, model, details):
    graph = {identifier: thing for identifier, thing in sorted(things.items())
             if model["kinds"][thing.kind]["home"] == "graph"}
    nodes = sorted((node_for(thing) for thing in graph.values()), key=lambda node: (node["name"].lower(), node["id"]))
    claims = [row for thing in graph.values() for row in thing.data.get("stands_in_for", [])]
    unverified = sum(thing.data["safety"]["state"] != "verified"
                     for thing in graph.values() if thing.kind == "ingredient")
    return {"nodes": nodes, "edges": [edge for thing in graph.values() for edge in edges_for(thing, model)],
            "answers": {identifier: queries.stand_ins(graph, identifier) for identifier, thing in graph.items()
                        if thing.kind == "recipe"}, "metadata": details, "counts": dict(Counter(thing.kind for thing in graph.values())),
            "claims": {"positive": sum(row["allows"] for row in claims), "exclusions": sum(not row["allows"] for row in claims)},
            "unverified": unverified}


def git_value(root, arguments):
    result = subprocess.run(["git", "-C", str(root)] + arguments, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return result.stdout.strip()
    return ""


def metadata(root):
    return {"commit": git_value(root, ["rev-parse", "HEAD"]), "branch": git_value(root, ["branch", "--show-current"])}


def page(root, data):
    assets = Path(root, "viewer")
    text = (assets / "index.html").read_text(encoding="utf-8")
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    for marker, content in (("__GRAPH_STYLES__", (assets / "style.css").read_text(encoding="utf-8")),
                            ("__GRAPH_RENDERER__", (assets / "graph.js").read_text(encoding="utf-8")),
                            ("__GRAPH_CONTROLS__", (assets / "controls.js").read_text(encoding="utf-8")),
                            ("__GRAPH_DATA__", encoded)):
        text = text.replace(marker, content)
    return text


def main(root, arguments=None, assets=None):
    parser = argparse.ArgumentParser(description="Build and open the graph's internal review page.")
    parser.add_argument("--no-open", action="store_true", help="write out/graph.html without opening a browser")
    options = parser.parse_args(arguments)
    things, issues = check.read_repository(root)
    if issues:
        print("view: graph has %d issues; run ./check" % len(issues), file=sys.stderr)
        return 1
    model, _ = reading.read_schema(assets or root)
    data = payload(things, model, metadata(root))
    destination = Path(root, "out", "graph.html").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page(assets or root, data), encoding="utf-8")
    print("Built %d graph entries: %s" % (len(data["nodes"]), destination))
    if options.no_open:
        return 0
    if webbrowser.open(destination.as_uri(), new=2):
        print("Opened %s" % destination.as_uri())
    else:
        print("Browser could not open automatically. Open %s" % destination.as_uri())
    return 0
