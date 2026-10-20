"""release: write one immutable, checksummed artifact of the graph, and refuse a production build that has not earned it.

The artifact holds the files of `graph/` and nothing else: never a probe, never a held-back word, never a generated page.
The same files always give the same bytes and the same hash. The time of the build is in the manifest only.
"""

import argparse
import datetime
import hashlib
import json
import os
import subprocess
from collections import namedtuple

from tools import check, numbers, review_rules, serving

ARTIFACT_SCHEMA_VERSION = 3
CHANNELS = ("draft", "production")
OUT = os.path.join("out", "release")
ARTIFACT_FILE = "graph-artifact.json"
MANIFEST_FILE = "manifest.json"
VECTORS_FILE = "serving-vectors.json"
SUMS_FILE = "SHA256SUMS"

GATE_TIERS = "every included thing is at tier reviewed or higher"
GATE_SAFETY = "every included ingredient has its safety verified by a person"
GATE_SAFETY_POINTS = "no recipe step has an open safety point"
GATE_REVIEW = "a live review record exists"
TIERS = ("drafted", "sourced", "reviewed", "verified", "cook-tested")
REVIEWED = TIERS.index("reviewed")

# Where a build comes from: the commit, the day it was made, and when this release was built.
Source = namedtuple("Source", ["commit", "date", "built_at"])
Gate = namedtuple("Gate", ["name", "passed", "detail"])


class Refused(Exception):
    """A production build whose gates do not all pass."""

    def __init__(self, gates):
        super().__init__("production is refused: " + "; ".join(gate.name for gate in gates))
        self.gates = gates


class Unreadable(Exception):
    """A graph with issues: nothing is released from it."""

    def __init__(self, issues):
        super().__init__("the graph has %d issues" % len(issues))
        self.issues = issues


def included_things(things):
    """The things whose files live in `graph/`."""
    return {thing_id: thing for thing_id, thing in things.items() if thing.path.startswith("graph/")}


def artifact_of(things, channel="draft"):
    """The channel is inside the artifact, so a checksum of the artifact covers it and a manifest cannot change it."""
    included = included_things(things)
    return {
        "artifactSchemaVersion": ARTIFACT_SCHEMA_VERSION,
        "channel": channel,
        "things": {thing_id: included[thing_id].data for thing_id in sorted(included)},
        "serving": serving.serving_of(included),
    }


def encode(artifact):
    """The one way the artifact is written: sorted keys, no spaces, UTF-8, a closing newline."""
    text = json.dumps(artifact, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def sha256_of(content):
    return hashlib.sha256(content).hexdigest()


def tier_gate(things):
    low = sorted(thing_id for thing_id, thing in things.items() if "tier" in thing.data and TIERS.index(thing.data["tier"]) < REVIEWED)
    return Gate(GATE_TIERS, not low, "%d things are below reviewed" % len(low))


def safety_gate(things):
    open_ones = sorted(thing_id for thing_id, thing in things.items() if thing.kind == "ingredient" and thing.data["safety"]["state"] != "verified")
    return Gate(GATE_SAFETY, not open_ones, "%d ingredients are not verified" % len(open_ones))


def safety_points_gate(things):
    count = numbers.count_safety_points(things)
    return Gate(GATE_SAFETY_POINTS, count == 0, "%d safety points are open" % count)


def review_gate(things):
    live = review_rules.live_records(things)
    return Gate(GATE_REVIEW, bool(live), "%d live review records" % len(live))


def gates_of(things):
    """Every production gate over what would be included, in a fixed order."""
    included = included_things(things)
    return [tier_gate(included), safety_gate(included), safety_points_gate(included), review_gate(included)]


def graph_version(source):
    """The date of the commit and its first seven letters, such as 2026.10.11-1102817."""
    return "%s-%s" % (source.date.replace("-", "."), source.commit[:7])


def facts_of(things):
    return sorted(thing_id for thing_id, thing in included_things(things).items() if thing.kind == "fact")


def manifest_of(things, encoded, channel, source):
    included = included_things(things)
    return {
        "artifactSchemaVersion": ARTIFACT_SCHEMA_VERSION,
        "graphVersion": graph_version(source),
        "sourceCommit": source.commit,
        "channel": channel,
        "contentSha256": sha256_of(encoded),
        "builtAt": source.built_at,
        "gates": [{"name": gate.name, "passed": gate.passed, "detail": gate.detail} for gate in gates_of(things)],
        "counts": {"things": numbers.count_things(included), "safety": numbers.count_safety(included)},
        "facts": facts_of(things),
    }


def write_file(folder, name, content):
    with open(os.path.join(folder, name), "wb") as handle:
        handle.write(content)


def sums_of(files):
    """A SHA256SUMS file that `shasum -c` reads: a hash, two spaces, a name."""
    lines = ["%s  %s" % (sha256_of(content), name) for name, content in sorted(files.items())]
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_release(root, channel, source):
    """Read the graph strictly, check the channel's gates, and write the files. Returns the manifest."""
    if channel not in CHANNELS:
        raise ValueError("the channel is one of %s" % ", ".join(CHANNELS))
    things, issues = check.read_repository(root)
    if issues:
        raise Unreadable(issues)
    failing = [gate for gate in gates_of(things) if not gate.passed]
    if channel == "production" and failing:
        raise Refused(failing)
    encoded = encode(artifact_of(things, channel))
    manifest = encode(manifest_of(things, encoded, channel, source))
    vectors = encode(serving.vectors_of(included_things(things)))
    folder = os.path.join(root, OUT)
    os.makedirs(folder, exist_ok=True)
    files = {ARTIFACT_FILE: encoded, MANIFEST_FILE: manifest, VECTORS_FILE: vectors}
    for name, content in files.items():
        write_file(folder, name, content)
    write_file(folder, SUMS_FILE, sums_of(files))
    return json.loads(manifest)


def git_output(root, *arguments):
    try:
        done = subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return done.stdout.strip()


def source_from_git(root, built_at):
    """The commit and its day, or None when the folder is no git checkout."""
    commit = git_output(root, "rev-parse", "HEAD")
    date = git_output(root, "show", "-s", "--format=%cs", "HEAD")
    if not commit or not date:
        return None
    return Source(commit, date, built_at)


def now_text():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def total_things(manifest):
    return sum(sum(tiers.values()) for tiers in manifest["counts"]["things"].values())


def report_refusal(refused):
    print("release: production is refused. These gates fail:")
    for gate in refused.gates:
        print("  - %s (%s)" % (gate.name, gate.detail))


def report_issues(unreadable):
    for issue in unreadable.issues[:20]:
        print("%s: %s [%s]" % (issue.path, issue.message, issue.rule))
    print("release: the graph has %d issues. Run ./check." % len(unreadable.issues))


def main(root, argv=None, source=None):
    parser = argparse.ArgumentParser(prog="release", description="Write the graph's release artifact to out/release.")
    parser.add_argument("--channel", choices=CHANNELS, default="draft")
    channel = parser.parse_args(argv).channel
    source = source or source_from_git(root, now_text())
    if source is None:
        print("release: this folder is no git checkout, so the artifact has no commit to name.")
        return 1
    try:
        manifest = write_release(root, channel, source)
    except Refused as refused:
        report_refusal(refused)
        return 1
    except Unreadable as unreadable:
        report_issues(unreadable)
        return 1
    print("release: %s %s, %d things, sha256 %s" % (manifest["channel"], manifest["graphVersion"], total_things(manifest), manifest["contentSha256"]))
    print("release: written to %s" % os.path.join(root, OUT))
    return 0
