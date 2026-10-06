"""Writes a thing to its file, in the one way a file is written.

Two spaces of indent. A statement, an amount or a list of ids sits on one
line when it fits, so a file reads like a card and a change shows as one line
in a diff. Sentences take a line each. The checker holds every file to this.
"""

import json
import os

from tools import reading

WIDTH = 100
INDENT = "  "


def is_plain(value):
    return not isinstance(value, (dict, list))


def is_word(value):
    """A plain value with no space in it: an id, a slug, a word or a number."""
    return is_plain(value) and not (isinstance(value, str) and " " in value)


def on_one_line(value):
    return json.dumps(value, ensure_ascii=False)


def write_value(value, depth, room):
    """The text of a value written at this depth, with this much room left on its first line."""
    if isinstance(value, dict):
        return write_object(value, depth, room)
    if isinstance(value, list):
        return write_list(value, depth, room)
    return on_one_line(value)


def write_object(value, depth, room):
    if not value:
        return "{}"
    holds_plain_values_only = all(is_plain(inner) for inner in value.values())
    if depth > 0 and holds_plain_values_only and len(on_one_line(value)) <= room:
        return on_one_line(value)
    lines = []
    for name, inner in value.items():
        lead = INDENT * (depth + 1) + json.dumps(name) + ": "
        lines.append(lead + write_value(inner, depth + 1, WIDTH - len(lead) - 1))
    return "{\n" + ",\n".join(lines) + "\n" + INDENT * depth + "}"


def write_list(value, depth, room):
    if not value:
        return "[]"
    if all(is_word(inner) for inner in value):
        return write_words(value, depth, room)
    lead = INDENT * (depth + 1)
    lines = [lead + write_value(inner, depth + 1, WIDTH - len(lead) - 1) for inner in value]
    return "[\n" + ",\n".join(lines) + "\n" + INDENT * depth + "]"


def write_words(words, depth, room):
    """A list of words on one line, or wrapped like a paragraph when it is too long for one."""
    if len(on_one_line(words)) <= room:
        return on_one_line(words)
    lead = INDENT * (depth + 1)
    lines = [lead]
    for index, word in enumerate(words):
        piece = on_one_line(word)
        if index < len(words) - 1:
            piece += ","
        if lines[-1] != lead and len(lines[-1]) + 1 + len(piece) > WIDTH:
            lines.append(lead)
        if lines[-1] != lead:
            lines[-1] += " "
        lines[-1] += piece
    return "[\n" + "\n".join(lines) + "\n" + INDENT * depth + "]"


def as_text(data):
    """A thing as the text of its file."""
    return write_object(data, 0, WIDTH) + "\n"


def write_thing(root, data):
    """Write a thing to the place its id names. Return that place."""
    model, _ = reading.read_schema(root)
    kind = reading.kind_of(data["id"])
    path = "%s/%s.json" % (model["kinds"][kind]["home"], data["id"])
    full = os.path.join(root, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as handle:
        handle.write(as_text(data))
    return path


def tidy(root):
    """Rewrite every file that is JSON but not written the one way. Return the files rewritten."""
    rewritten = []
    for path in reading.file_paths(root):
        full = os.path.join(root, path)
        with open(full, encoding="utf-8") as handle:
            text = handle.read()
        try:
            data = json.loads(text)
        except ValueError:
            continue
        if text != as_text(data):
            with open(full, "w", encoding="utf-8") as handle:
                handle.write(as_text(data))
            rewritten.append(path)
    return rewritten
