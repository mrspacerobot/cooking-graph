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


def fact(slug, english, means, also=()):
    thing = head("fact/" + slug, english)
    if also:
        thing["aliases"] = {"en": list(also)}
    thing["means"] = means
    thing["concern"] = "allergen"
    thing["regulated"] = []
    return thing


def source():
    return {
        "id": "source/kitchen-law",
        "tier": DRAFTED,
        "title": "The law of the small kitchen",
        "publisher": "The small kitchen",
        "url": "https://example.org/law",
        "read_on": "2026-10-07",
        "reuse": "Free to reuse with the source named (section 3).",
        "commercial_use": "allowed",
        "taken": "The 2 facts of the kitchen.",
    }


def holds(fact_id, certain=True):
    return {"fact": fact_id, "basis": "It is made of it.", "certain": certain}


def group(slug, english, within=None, stands_alone=None):
    thing = head("group/" + slug, english)
    thing["shares"] = "They soften slowly and turn sweet."
    thing["within"] = link(within) if within else None
    thing["stands_alone"] = stands_alone
    return thing


def counting(thing, plural):
    """A food with a plural is countable; a food with none is uncountable."""
    thing["plurals"] = {} if plural is None else {"en": plural}
    thing["uncountable"] = plural is None
    return thing


def ingredient(slug, english, contains, free_of, is_a=(), part_of=(), groups=(), plural=None):
    thing = counting(head("ingredient/" + slug, english), plural)
    thing["is_a"] = [link(parent) for parent in is_a]
    thing["part_of"] = [link(whole) for whole in part_of]
    thing["groups"] = [link(one) for one in groups]
    thing["forms"] = []
    thing["behaviour"] = "Softens over gentle heat."
    thing["safety"] = {
        "state": "unverified",
        "contains": [holds(one) for one in contains],
        "free_of": list(free_of),
        "note": None,
    }
    thing["stands_in_for"] = []
    thing["in_pantry_of"] = [link("cuisine/french")]
    thing["same_as"] = []
    return thing


def technique(slug, english):
    thing = head("technique/" + slug, english)
    thing["does"] = "Softens cut vegetables in fat over low heat."
    thing["how"] = ["Warm the fat over low heat.", "Stir now and then until soft."]
    thing["cues"] = [{"sense": "see", "text": "The pieces turn glassy."}]
    thing["mistakes"] = [{"mistake": "The heat is too high.", "fix": "Turn it down."}]
    thing["works_on"] = [link("group/vegetables")]
    thing["makes"] = [link("form/minced")]
    thing["needs"] = [
        {"role": "vessel", "options": ["equipment/pan"], "tier": DRAFTED},
        {"role": "fat", "options": ["ingredient/butter", "preparation/roux"], "tier": DRAFTED},
    ]
    thing["comes_after"] = []
    thing["variant_of"] = []
    thing["belongs_to"] = [link("cuisine/french")]
    return thing


def part(part_id, role, options, optional=False):
    return {"id": part_id, "role": role, "options": list(options), "optional": optional, "tier": DRAFTED}


def dish():
    thing = head("dish/buttered-onions", "Buttered onions")
    thing["is"] = "Onions softened slowly in butter."
    thing["parts"] = [
        part("onion", "main", ["ingredient/onion"]),
        part("roux", "fat", ["preparation/roux"]),
        part("garnish", "main", ["ingredient/onion-skin"], optional=True),
    ]
    thing["teaches"] = [link("technique/sweat")]
    thing["belongs_to"] = [link("cuisine/french")]
    thing["same_as"] = []
    return thing


def preparation():
    thing = counting(head("preparation/roux", "Roux"), None)
    thing["is"] = "Flour cooked in butter."
    thing["parts"] = [part("butter", "fat", ["ingredient/butter"]), part("flour", "main", ["ingredient/flour"], optional=True)]
    thing["groups"] = []
    thing["teaches"] = [link("technique/sweat")]
    thing["stands_in_for"] = [
        link("ingredient/flour", allows=True, when=["technique/sweat"], not_when=[], ratio=None, caveat="It is already cooked.")
    ]
    thing["belongs_to"] = [link("cuisine/french")]
    thing["same_as"] = []
    return thing


def by_product():
    """A preparation with no parts of its own: it is whatever a step leaves behind."""
    thing = counting(head("preparation/onion-juices", "Onion juices"), None)
    thing["is"] = "The sweet liquid onions leave in the pan."
    thing["parts"] = []
    thing["groups"] = [link("group/alliums")]
    thing["teaches"] = []
    thing["stands_in_for"] = []
    thing["belongs_to"] = []
    thing["same_as"] = []
    return thing


def recipe():
    thing = head("recipe/buttered-onions", "Buttered onions")
    thing["makes"] = "dish/buttered-onions"
    thing["yields"] = {"value": 2, "unit": "serving"}
    thing["ingredients"] = [
        {"thing": "ingredient/onion", "amount": {"value": 2, "unit": "piece"}, "forms": ["form/minced"], "part": "onion"},
        {"thing": "ingredient/butter", "amount": {"value": 20, "unit": "gram"}, "forms": [], "part": "roux"},
    ]
    thing["equipment"] = ["equipment/pan"]
    thing["steps"] = [
        {
            "technique": "technique/sweat",
            "works_on": ["ingredient/onion"],
            "with": ["ingredient/butter"],
            "text": "Soften the {onion} in the {roux} over low heat.",
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
    held_back = probes.held_back_ids(["dish-probe/" + slug for slug in slugs], never=["dish-probe/buttered-onions"])
    files = {}
    for slug, name in zip(slugs, PROBED_DISHES):
        probe_id = "dish-probe/" + slug
        files["probes/dish-probe/" + slug + ".json"] = {
            "id": probe_id,
            "tier": DRAFTED,
            "batch": BATCH,
            "set": "held-back" if probe_id in held_back else "growing",
            "written_by": "another-model",
            "cuisine": "french",
            "written_for": "sweating",
            "dish": name,
            "also_called": [],
            "techniques": ["sweat"],
            "ingredients": ["onion", "butter"],
        }
    files.update(safety_probe_files())
    return files


# By the hash, the one in five held back here is the onion gratin: the dish that is in the graph stays in view.
SAFETY_PROBED = ["Buttered onions", "Onion tart", "Onion soup", "Creamed onions", "Onion gratin"]


def safety_probe_files():
    slugs = [name.lower().replace(" ", "-") for name in SAFETY_PROBED]
    held_back = probes.held_back_ids(["safety-probe/" + slug for slug in slugs])
    files = {}
    for slug, name in zip(slugs, SAFETY_PROBED):
        probe_id = "safety-probe/" + slug
        files["probes/safety-probe/" + slug + ".json"] = {
            "id": probe_id,
            "tier": DRAFTED,
            "batch": "safety-1",
            "set": "held-back" if probe_id in held_back else "growing",
            "written_by": "another-model",
            "dish": name,
            "also_called": [],
            "holds": ["milk"],
            "does_not_hold": ["gluten"],
            "why": "It is made with butter and no flour.",
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
        source(),
        fact("dairy", "Dairy", "Milk, or anything made from it.", also=["milk"]),
        fact("gluten", "Gluten", "Wheat, barley or rye, or anything made from them."),
        french,
        provencal,
        pan,
        minced,
        group("vegetables", "Vegetables"),
        group("alliums", "Alliums", within="group/vegetables"),
        ingredient("allium", "Allium", [], ["fact/dairy", "fact/gluten"], groups=["group/alliums"]),
        ingredient("onion", "Onion", [], ["fact/dairy", "fact/gluten"], is_a=["ingredient/allium"], groups=["group/alliums"],
                   plural="Onions"),
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


def reviewer(slug="owner", kind="person", knows=(("cuisine/french", "cooks-it-at-home"),), model_id=None, safety_authority=None):
    return {
        "id": "reviewer/" + slug,
        "kind": kind,
        "model_id": model_id,
        "knows": [{"cuisine": cuisine, "how": how} for cuisine, how in knows],
        "safety_authority": safety_authority,
        "added_on": "2026-10-14",
    }


def cover(thing, seen, verdict="approved", field=None, target=None, note=None):
    return {"thing": thing, "field": field, "target": target, "seen": seen, "verdict": verdict, "note": note}


def review(slug, reviewer_slug, grants, covers, cuisine="cuisine/french", mode="rows", against=None, supersedes=(),
           rulings=(), on="2026-10-14", sample=None, note=None):
    against = against or [{"how": "own-knowledge", "source": None, "note": "Cooked it at home."}]
    return {
        "id": "review/" + slug,
        "reviewer": "reviewer/" + reviewer_slug,
        "on": on,
        "grants": grants,
        "cuisine": cuisine,
        "mode": mode,
        "sample": sample,
        "against": against,
        "covers": covers,
        "rulings": list(rulings),
        "supersedes": ["review/" + earlier for earlier in supersedes],
        "note": note,
    }


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

    def add(self, content):
        """Add a new thing to the kitchen at the place its id names, and remember it so that `change` can edit it."""
        kind, slug = content["id"].split("/")
        path = "graph/%s/%s.json" % (kind, slug)
        self.files[path] = content
        self.write(path, content)
        return path

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
