"""Documents a command writes from the files. The check refuses one that has fallen behind.

Each is written by `./safety <word> > <path>`. Nobody edits them by hand.
"""

import os

from tools import safety_probes, strictness
from tools.reading import Issue


def strict_answers(things):
    return strictness.document(things)


def safety_disagreements(things):
    return safety_probes.disagreements_document(safety_probes.run(things))


# The path of each document, the word that writes it, and how it is made.
DOCUMENTS = {
    "docs/strict-answers.md": ("strict", strict_answers),
    "docs/safety-disagreements.md": ("disagreements", safety_disagreements),
}


def behind(root, things):
    """An issue for each written document that exists and no longer says what the files say."""
    issues = []
    for path, (word, make) in sorted(DOCUMENTS.items()):
        full = os.path.join(root, path)
        if not os.path.exists(full):
            continue
        with open(full, encoding="utf-8") as handle:
            if handle.read() != make(things):
                message = "has fallen behind the files: run ./safety %s > %s" % (word, path)
                issues.append(Issue(path, "", "not-current", message))
    return issues
