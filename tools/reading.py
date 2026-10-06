"""Finds the files of the repository and reads them strictly."""

import json
import os
import re
from collections import namedtuple

# One thing the checker found: the file, the place inside it, the rule and a sentence for a person.
Issue = namedtuple("Issue", ["path", "where", "rule", "message"])

# One file that was read: where it lives, its kind, and its content (None when it could not be read).
Thing = namedtuple("Thing", ["path", "kind", "data"])

HOMES = ("graph", "probes")
SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class DuplicateField(ValueError):
    """A JSON object that writes one field twice."""


def _fields_once(pairs):
    fields = {}
    for name, value in pairs:
        if name in fields:
            raise DuplicateField(name)
        fields[name] = value
    return fields


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=_fields_once)


def read_schema(root):
    """The model and the closed word lists the files are checked against."""
    model = read_json(os.path.join(root, "schema", "model.json"))
    words = read_json(os.path.join(root, "schema", "words.json"))
    return model, words


def is_slug(text):
    return isinstance(text, str) and SLUG.match(text) is not None


def is_id(text, kinds):
    """An id is a kind and a slug, such as technique/deglaze."""
    if not isinstance(text, str) or text.count("/") != 1:
        return False
    kind, slug = text.split("/")
    return kind in kinds and is_slug(slug)


def kind_of(thing_id):
    return thing_id.split("/")[0]


def file_paths(root):
    """Every file under the homes, relative to the root, in a fixed order."""
    found = []
    for home in HOMES:
        for folder, _, names in os.walk(os.path.join(root, home)):
            for name in names:
                if not name.startswith("."):
                    path = os.path.relpath(os.path.join(folder, name), root)
                    found.append(path.replace(os.sep, "/"))
    return sorted(found)


def join(where, name):
    """The place of a field inside a place: steps[0] and text give steps[0].text."""
    if where == "":
        return name
    return where + "." + name


def nested(value, where=""):
    """Every object inside a value, each with the place it sits at."""
    if isinstance(value, dict):
        yield where, value
        for name, inner in value.items():
            yield from nested(inner, join(where, name))
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            yield from nested(inner, "%s[%d]" % (where, index))
