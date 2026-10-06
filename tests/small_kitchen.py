"""A tiny, valid repository for the tests.

It holds one or two things of every kind, written in the real schema, so a test
can break exactly one rule in one file and see the checker name it. When the
model changes, this is the one place in the tests that changes with it.
"""

import copy
import os
import shutil
import tempfile

from tools import probes, writing

REPOSITORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTED = "drafted"
BATCH = "sweating-1"


def link(thing, **more):
    row = {"thing": thing}
    row.update(more)
    row["tier"] = DRAFTED
    return row


def head(thing_id, english):
    return {"id": thing_id, "tier": DRAFTED, "names": {"en": english}, "aliases": {}}


def fact(slug, english, means):
    thing = head("fact/" + slug, english)
    thing["means"] = means
    return thing


def ingredient(slug, english, contains, free_of, is_a=(), part_of=()):
    thing = head("ingredient/" + slug, english)
    thing["is_a"] = [link(parent) for parent in is_a]
    thing["part_of"] = [link(whole) for whole in part_of]
    thing["forms"] = []
    thing["behaviour"] = "Softens over gentle heat."
    thing["safety"] = {
        "state": "unverified",
        "contains": list(contains),
        "free_of": list(free_of),
        "note": None,
    }
    thing["stands_in_for"] = []
    thing["in_pantry_of"] = [link("cuisine/french")]
    return thing


def technique(slug, english):
    thing = head("technique/" + slug, english)
    thing["does"] = "Softens cut vegetables in fat over low heat."
    thing["how"] = ["Warm the fat over low heat.", "Stir now and then until soft."]
    thing["cues"] = [{"sense": "see", "text": "The pieces turn glassy."}]
    thing["mistakes"] = [{"mistake": "The heat is too high.", "fix": "Turn it down."}]
    thing["works_on"] = [link("ingredient/onion")]
    thing["makes"] = [link("form/minced")]
    thing["needs"] = [
        {"role": "vessel", "options": ["equipment/pan"], "tier": DRAFTED},
        {"role": "fat", "options": ["ingredient/butter", "preparation/roux"], "tier": DRAFTED},
    ]
    thing["comes_after"] = []
    thing["variant_of"] = []
    thing["belongs_to"] = [link("cuisine/french")]
    return thing


def part(role, options):
    return {"role": role, "options": list(options), "tier": DRAFTED}


def dish():
    thing = head("dish/buttered-onions", "Buttered onions")
    thing["is"] = "Onions softened slowly in butter."
    thing["parts"] = [part("main", ["ingredient/onion"]), part("fat", ["preparation/roux"])]
    thing["teaches"] = [link("technique/sweat")]
    thing["belongs_to"] = [link("cuisine/french")]
    return thing


def preparation():
    thing = head("preparation/roux", "Roux")
    thing["is"] = "Flour cooked in butter."
    thing["parts"] = [part("fat", ["ingredient/butter"]), part("main", ["ingredient/flour"])]
    thing["teaches"] = [link("technique/sweat")]
    thing["belongs_to"] = [link("cuisine/french")]
    return thing


def by_product():
    """A preparation with no parts of its own: it is whatever a step leaves behind."""
    thing = head("preparation/onion-juices", "Onion juices")
    thing["is"] = "The sweet liquid onions leave in the pan."
    thing["parts"] = []
    thing["teaches"] = []
    thing["belongs_to"] = []
    return thing


def recipe():
    thing = head("recipe/buttered-onions", "Buttered onions")
    thing["makes"] = "dish/buttered-onions"
    thing["yields"] = {"value": 2, "unit": "serving"}
    thing["ingredients"] = [
        {"thing": "ingredient/onion", "amount": {"value": 2, "unit": "piece"}, "forms": ["form/minced"]},
        {"thing": "ingredient/butter", "amount": {"value": 20, "unit": "gram"}, "forms": []},
    ]
    thing["equipment"] = ["equipment/pan"]
    thing["steps"] = [
        {
            "technique": "technique/sweat",
            "works_on": ["ingredient/butter", "ingredient/onion"],
            "text": "Soften the onions in the butter over low heat.",
            "time": {"from": 8, "to": 10, "unit": "minute"},
            "temperature": None,
            "safety_points": ["cooling-and-keeping"],
            "makes": [],
        }
    ]
    return thing


def program():
    thing = head("program/small-program", "Small program")
    level = {
        "number": 1,
        "names": {"en": "Sweat an onion"},
        "teaches": [link("technique/sweat")],
        "through": [link("dish/buttered-onions")],
    }
    skill = {"slug": "sweating", "names": {"en": "Sweating"}, "comes_after": [], "levels": [level]}
    second = {
        "slug": "mincing",
        "names": {"en": "Mincing"},
        "comes_after": [{"skill": "sweating", "tier": DRAFTED}],
        "levels": [{"number": 1, "names": {"en": "Mince"}, "teaches": [], "through": []}],
    }
    thing["belongs_to"] = [link("cuisine/french")]
    thing["courses"] = [{"slug": "basics", "names": {"en": "Basics"}, "skills": [skill, second]}]
    return thing


PROBED_DISHES = ["Buttered onions", "Onion tart", "Onion soup", "Creamed onions", "Glazed onions"]


def probe_files():
    slugs = [name.lower().replace(" ", "-") for name in PROBED_DISHES]
    held_back = probes.held_back_ids(["dish-probe/" + slug for slug in slugs])
    files = {}
    for slug, name in zip(slugs, PROBED_DISHES):
        probe_id = "dish-probe/" + slug
        files["probes/dish-probe/" + slug + ".json"] = {
            "id": probe_id,
            "tier": DRAFTED,
            "batch": BATCH,
            "set": "held-back" if probe_id in held_back else "growing",
            "written_for": "sweating",
            "dish": name,
            "also_called": [],
            "techniques": ["sweat"],
            "ingredients": ["onion", "butter"],
        }
    return files


def graph_files():
    french = head("cuisine/french", "French")
    french["within"] = None
    provencal = head("cuisine/provencal", "Provencal")
    provencal["within"] = link("cuisine/french")
    pan = head("equipment/pan", "Pan")
    pan["use"] = "Cooking over a flame."
    minced = head("form/minced", "Minced")
    minced["looks_like"] = "Very small, uneven pieces."
    minced["size"] = [{"measure": "side", "length": {"from": 1, "to": 2, "unit": "millimetre"}}]
    mince = technique("mince", "Mince")
    mince["comes_after"] = [link("technique/sweat", why="A soft onion is easier to judge.")]
    things = [
        fact("dairy", "Dairy", "Milk, or anything made from it."),
        fact("gluten", "Gluten", "Wheat, barley or rye, or anything made from them."),
        french,
        provencal,
        pan,
        minced,
        ingredient("allium", "Allium", [], ["fact/dairy", "fact/gluten"]),
        ingredient("onion", "Onion", [], ["fact/dairy", "fact/gluten"], is_a=["ingredient/allium"]),
        ingredient("onion-skin", "Onion skin", [], ["fact/dairy", "fact/gluten"], part_of=["ingredient/onion"]),
        ingredient("butter", "Butter", ["fact/dairy"], ["fact/gluten"]),
        ingredient("flour", "Flour", ["fact/gluten"], ["fact/dairy"]),
        technique("sweat", "Sweat"),
        mince,
        preparation(),
        by_product(),
        dish(),
        recipe(),
        program(),
    ]
    return {"graph/" + thing["id"] + ".json": thing for thing in things}


class SmallKitchen:
    """The tiny repository on disk, in a folder of its own."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="small-kitchen-")
        shutil.copytree(os.path.join(REPOSITORY, "schema"), os.path.join(self.root, "schema"))
        self.files = {}
        self.files.update(graph_files())
        self.files.update(probe_files())
        for path, content in self.files.items():
            self.write(path, content)

    def write(self, path, content):
        self.write_text(path, writing.as_text(content))

    def write_text(self, path, text):
        full = os.path.join(self.root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def change(self, path, change):
        """Rewrite one file after `change` has altered a copy of its content."""
        content = copy.deepcopy(self.files[path])
        change(content)
        self.write(path, content)

    def remove(self, path):
        os.remove(os.path.join(self.root, path))

    def held_back_path(self):
        for path, content in sorted(self.files.items()):
            if content.get("set") == "held-back":
                return path
        raise AssertionError("the small kitchen holds no held-back probe")

    def close(self):
        shutil.rmtree(self.root)
