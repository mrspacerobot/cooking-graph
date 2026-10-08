"""The command line for the three graph questions. Reject a broken graph in full."""

import argparse
import json
import sys

from tools import check, queries


def build_parser(command):
    parser = argparse.ArgumentParser(prog=command, description=queries.SAFETY)
    if command == "compose":
        parser.add_argument("--technique", action="append", required=True,
                            help="technique id or name; repeat for several techniques")
        parser.add_argument("--servings", type=float, help="scale the amounts to this many servings")
        parser.add_argument("--top", type=int, default=5, help="how many recipes to return, best first")
        parser.add_argument("at_home", nargs="*", help="ingredients or preparations at home, as ids or quoted names")
    else:
        parser.add_argument("subject", help="a recipe for stand-ins, a technique for recipes or kitchen; id or name")
    if command == "kitchen":
        parser.add_argument("at_home", nargs="*", help="ingredients or preparations at home, as ids or quoted names")
    if command != "recipes":
        parser.add_argument("--avoid", action="append", default=[], help="fact id or name; repeat for several facts")
    return parser


def main(root, command):
    parser = build_parser(command)
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
        elif command == "compose":
            answer = queries.compose(things, args.technique, args.at_home, args.avoid, args.servings, args.top)
        else:
            answer = queries.kitchen(things, args.subject, args.at_home, args.avoid)
    except ValueError as error:
        print("%s: %s" % (command, error), file=sys.stderr)
        return 1
    print(json.dumps(answer, ensure_ascii=False, sort_keys=True, indent=2))
    return 0
