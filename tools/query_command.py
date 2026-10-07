"""The command line for the three graph questions. Reject a broken graph in full."""

import argparse
import json
import sys

from tools import check, queries


def main(root, command):
    parser = argparse.ArgumentParser(prog=command, description=queries.SAFETY)
    parser.add_argument("subject", help="a recipe for stand-ins, a technique for recipes or kitchen; id or name")
    if command == "kitchen":
        parser.add_argument("at_home", nargs="*", help="ingredients or preparations at home, as ids or quoted names")
    if command != "recipes":
        parser.add_argument("--avoid", action="append", default=[], help="fact id or name; repeat for several facts")
    args = parser.parse_args()
    things, issues = check.read_repository(root)
    if issues:
        print("%s: graph has %d issues; run ./check" % (command, len(issues)), file=sys.stderr)
        return 1
    try:
        if command == "stand-ins":
            answer = queries.stand_ins(things, args.subject, args.avoid)
        elif command == "recipes":
            answer = queries.recipes(things, args.subject)
        else:
            answer = queries.kitchen(things, args.subject, args.at_home, args.avoid)
    except ValueError as error:
        print("%s: %s" % (command, error), file=sys.stderr)
        return 1
    print(json.dumps(answer, ensure_ascii=False, sort_keys=True, indent=2))
    return 0
