"""Copy new files of the graph from another checkout into this one, and refuse any that clash.

A worktree is checked alone, so two worktrees can each add the same
ingredient and both pass. This is where they meet. A file is copied only when
its id is new and no name or alias of it is held by another thing of its
family, in the graph or among the files coming in. A file that exists here
and differs is reported and never overwritten.
"""

import json
import os
from collections import namedtuple

from tools import names

Result = namedtuple("Result", ["copied", "changed", "refused"])
FOOD = ("ingredient", "preparation")


def family(kind):
    return "food" if kind in FOOD else kind


def graph_files(root):
    found = {}
    base = os.path.join(root, "graph")
    if not os.path.isdir(base):
        return found
    for kind in sorted(os.listdir(base)):
        folder = os.path.join(base, kind)
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            if name.endswith(".json"):
                found["graph/%s/%s" % (kind, name)] = os.path.join(folder, name)
    return found


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def holders(root):
    """Which file holds each plain name, within each family, in a checkout."""
    held = {}
    for relative, path in graph_files(root).items():
        kind = relative.split("/")[1]
        try:
            data = json.loads(read(path))
        except ValueError:
            continue
        for name in names.plain_names(data):
            held.setdefault((family(kind), name), set()).add(relative)
    return held


def merge(source, target, dry_run=False):
    here = graph_files(target)
    coming = graph_files(source)
    new = [relative for relative in coming if relative not in here]
    changed = [relative for relative in coming if relative in here and read(coming[relative]) != read(here[relative])]
    held = holders(target)
    incoming = {}
    for relative in new:
        kind = relative.split("/")[1]
        for name in names.plain_names(json.loads(read(coming[relative]))):
            incoming.setdefault((family(kind), name), []).append(relative)
    copied, refused = [], []
    for relative in new:
        kind = relative.split("/")[1]
        why = None
        for name in sorted(names.plain_names(json.loads(read(coming[relative])))):
            others = [path for path in held.get((family(kind), name), ()) if path != relative]
            others += [path for path in incoming[(family(kind), name)] if path != relative]
            if others:
                why = "the name '%s' is also held by %s" % (name, ", ".join(sorted(set(others))))
                break
        if why:
            refused.append((relative, why))
        else:
            copied.append(relative)
    if not dry_run:
        for relative in copied:
            destination = os.path.join(target, relative)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, "w", encoding="utf-8") as handle:
                handle.write(read(coming[relative]))
    return Result(copied, changed, refused)
