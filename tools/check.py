"""Reads every file strictly and lists every issue."""

import os
import unittest

from tools import group_rules, part_rules, probe_rules, reading, review_rules, rules, shapes, stand_in_rules, writing, written_documents
from tools.reading import Issue, Thing


def place_of(path, model):
    """The id a path stands for, or None when the path is no place for a thing."""
    parts = path.split("/")
    if len(parts) != 3 or not parts[2].endswith(".json"):
        return None
    home, kind, slug = parts[0], parts[1], parts[2][: -len(".json")]
    known = model["kinds"].get(kind)
    if known is None or known["home"] != home:
        return None
    return kind + "/" + slug


def read_content(root, path, issues):
    """The content of one file, or None with an issue when it cannot be read as JSON."""
    try:
        data = reading.read_json(os.path.join(root, path))
    except reading.DuplicateField as twice:
        issues.append(Issue(path, "", "duplicate-field", "the field '%s' is written twice" % twice))
        return None
    except ValueError as broken:
        issues.append(Issue(path, "", "not-json", "is not JSON: %s" % broken))
        return None
    with open(os.path.join(root, path), encoding="utf-8") as handle:
        if handle.read() != writing.as_text(data):
            issues.append(Issue(path, "", "not-tidy", "is not written the one way: run ./tidy"))
    return data


def read_files(root, model, issues):
    """Every file that sits where a thing may sit, by the id its path stands for."""
    files = {}
    for path in reading.file_paths(root):
        thing_id = place_of(path, model)
        if thing_id is None:
            issues.append(Issue(path, "", "bad-path", "a thing lives at <home>/<kind>/<slug>.json"))
        elif not reading.is_id(thing_id, model["kinds"]):
            issues.append(Issue(path, "", "bad-id", "the file name must be lowercase words joined by hyphens"))
        else:
            data = read_content(root, path, issues)
            files[thing_id] = Thing(path, reading.kind_of(thing_id), data)
    return files


def id_matches_path(thing_id, thing):
    """An issue when a file carries another id than the one its path stands for."""
    if not isinstance(thing.data, dict) or "id" not in thing.data or thing.data["id"] == thing_id:
        return []
    message = "the id must be '%s', after the place of the file" % thing_id
    return [Issue(thing.path, "id", "bad-id", message)]


def read_repository(root):
    """Read everything. Return the sound things by id, and every issue found, in a fixed order."""
    model, words = reading.read_schema(root)
    issues = []
    files = read_files(root, model, issues)
    kinds = {thing_id: thing.kind for thing_id, thing in files.items()}
    sound = {}
    for thing_id, thing in sorted(files.items()):
        if thing.data is None:
            continue
        found = shapes.check_thing(thing, model, words, kinds) + id_matches_path(thing_id, thing)
        issues.extend(found)
        if not found:
            sound[thing_id] = thing
    for rule in rules.BASE_RULES + group_rules.RULES + part_rules.RULES + probe_rules.RULES + stand_in_rules.RULES + review_rules.RULES:
        issues.extend(rule(sound))
    issues.extend(rules.foods_share_no_name(sound, reading.read_buy_or_make(root)))
    issues.extend(rules.model_document(root, model))
    if not issues:  # a written document is compared only with files that are sound
        issues.extend(written_documents.behind(root, sound))
    issues.extend(rules.em_dashes(root))
    return sound, sorted(issues)


def check_repository(root):
    return read_repository(root)[1]


def tests_pass(root):
    """Run the tests of the tools. A checker that is broken must not pass the files."""
    suite = unittest.defaultTestLoader.discover(os.path.join(root, "tests"), top_level_dir=root)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    return result.wasSuccessful()


def main(root):
    if not tests_pass(root):
        print("check: the tests of the tools fail. Fix them before anything else.")
        return 1
    things, issues = read_repository(root)
    for issue in issues:
        place = issue.path
        if issue.where:
            place = "%s: %s" % (issue.path, issue.where)
        print("%s: %s [%s]" % (place, issue.message, issue.rule))
    if issues:
        print("check: %d issues in %d files." % (len(issues), len({issue.path for issue in issues})))
        return 1
    print("check: %d files read strictly, no issue." % len(things))
    return 0
