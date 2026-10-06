"""Checks one file against the model, field by field.

The model (schema/model.json) says what each field may hold with a small
rule: {"is": "text"}, {"is": "ref", "kinds": [...]}, {"is": "list", "of": ...}.
Each kind of rule has one method here. Files are read strictly: an unknown
field, a missing field and a reference to nothing are all issues.
"""

from tools import names, sentences
from tools.reading import Issue, is_id, is_slug, join

EXACT_QUANTITY = {"value", "unit"}
RANGE_QUANTITY = {"from", "to", "unit"}
ROMANIZED = "-Latn"


def is_positive_number(value):
    is_number = isinstance(value, (int, float)) and not isinstance(value, bool)
    return is_number and value > 0


class ShapeCheck:
    def __init__(self, path, model, words, kinds):
        self.path = path
        self.model = model
        self.words = words
        self.kinds = kinds  # the kind of every file that exists, by id
        self.issues = []

    def report(self, where, rule, message):
        self.issues.append(Issue(self.path, where, rule, message))

    def check(self, value, rule, where):
        if value is None:
            if not rule.get("or_null"):
                self.report(where, "wrong-type", "must not be null")
            return
        checker = getattr(self, "check_" + rule["is"])
        checker(value, rule, where)

    def is_a(self, value, expected, where, name):
        if isinstance(value, expected) and not isinstance(value, bool):
            return True
        self.report(where, "wrong-type", "must be " + name)
        return False

    def check_id(self, value, rule, where):
        # The id is compared with the path where the file is read, in tools/check.py.
        self.is_a(value, str, where, "an id")

    def check_word(self, value, rule, where):
        if self.is_a(value, str, where, "a word") and value not in self.words[rule["from"]]:
            allowed = ", ".join(self.words[rule["from"]])
            self.report(where, "not-in-" + rule["from"], "'%s' is not one of: %s" % (value, allowed))

    def check_label(self, value, rule, where):
        if not self.is_a(value, str, where, "a string"):
            return
        if value == "" or value.strip() != value:
            self.report(where, "empty", "must be a name with no space around it")

    def check_text(self, value, rule, where):
        if not self.is_a(value, str, where, "a sentence"):
            return
        if value.strip() == "" or value.strip() != value:
            self.report(where, "empty", "must be a sentence with no space around it")
            return
        for broken_rule, message in sentences.issues_in(value, self.words):
            self.report(where, broken_rule, message)

    def check_slug(self, value, rule, where):
        if not is_slug(value):
            self.report(where, "bad-slug", "must be lowercase words joined by hyphens")

    def check_integer(self, value, rule, where):
        if not self.is_a(value, int, where, "a whole number"):
            return
        if "at_least" in rule and value < rule["at_least"]:
            self.report(where, "too-small", "must be at least %d" % rule["at_least"])

    def check_number(self, value, rule, where):
        if not is_positive_number(value):
            self.report(where, "wrong-type", "must be a number above zero")

    def check_ref(self, value, rule, where):
        if not is_id(value, self.model["kinds"]):
            self.report(where, "bad-id", "'%s' is not an id: a kind, a slash and a slug" % value)
        elif value not in self.kinds:
            self.report(where, "missing-reference", "'%s' does not exist" % value)
        elif self.kinds[value] not in rule["kinds"]:
            allowed = " or ".join(rule["kinds"])
            self.report(where, "wrong-kind", "'%s' must be a %s" % (value, allowed))

    def check_list(self, value, rule, where):
        if not self.is_a(value, list, where, "a list"):
            return
        if len(value) < rule.get("at_least", 0):
            self.report(where, "too-few", "needs at least %d" % rule["at_least"])
        seen = []
        for index, item in enumerate(value):
            place = "%s[%d]" % (where, index)
            if isinstance(item, str) and item in seen:
                self.report(place, "listed-twice", "'%s' is listed twice" % item)
            seen.append(item)
            self.check(item, rule["of"], place)

    def check_object(self, value, rule, where):
        if not self.is_a(value, dict, where, "an object"):
            return
        fields = rule["fields"]
        for name in value:
            if name not in fields:
                self.report(join(where, name), "unknown-field", "'%s' is not a field here" % name)
        for name, field_rule in fields.items():
            if name not in value:
                self.report(join(where, name), "missing-field", "'%s' is missing" % name)
            else:
                self.check(value[name], field_rule, join(where, name))
        written = [name for name in value if name in fields]
        if written != [name for name in fields if name in value]:
            self.report(where, "field-order", "fields must come in the order of the model")

    def check_shape(self, value, rule, where):
        self.check(value, self.model["shapes"][rule["name"]], where)

    def check_link(self, value, rule, where):
        """A statement: the thing it points at, what the model adds, and its tier."""
        fields = {"thing": {"is": "ref", "kinds": rule["to"]}}
        fields.update(rule.get("with", {}))
        fields["tier"] = {"is": "word", "from": "tiers"}
        self.check_object(value, {"fields": fields}, where)

    def check_quantity(self, value, rule, where):
        """A number with a unit: {"value", "unit"} or {"from", "to", "unit"}."""
        if not isinstance(value, dict) or set(value) not in (EXACT_QUANTITY, RANGE_QUANTITY):
            self.report(where, "bad-quantity", "must be value and unit, or from, to and unit")
            return
        if value["unit"] not in self.words[rule["units"]]:
            allowed = ", ".join(self.words[rule["units"]])
            self.report(where, "not-in-" + rule["units"], "'%s' is not one of: %s" % (value["unit"], allowed))
        numbers = [value[name] for name in value if name != "unit"]
        if not all(is_positive_number(number) for number in numbers):
            self.report(where, "bad-quantity", "must be numbers above zero")
        elif len(numbers) == 2 and value["from"] >= value["to"]:
            self.report(where, "bad-quantity", "a range must run from the smaller to the larger number")

    def check_language(self, tag, where):
        language = tag
        if tag.endswith(ROMANIZED):
            language = tag[: -len(ROMANIZED)]
        if language not in self.words["languages"]:
            self.report(where, "not-in-languages", "'%s' is not a language of the list" % tag)

    def check_names(self, value, rule, where):
        """One name per language. English is required. Another script brings its romanization."""
        if not self.is_a(value, dict, where, "names by language"):
            return
        if "en" not in value:
            self.report(where, "english-name-missing", "needs an English name")
        for tag, name in value.items():
            place = join(where, tag)
            self.check_language(tag, place)
            self.check_label(name, {}, place)
            needs_twin = isinstance(name, str) and not names.is_latin(name)
            if needs_twin and tag + ROMANIZED not in value:
                self.report(place, "romanization-missing", "needs its romanization as '%s%s'" % (tag, ROMANIZED))

    def check_aliases(self, value, rule, where):
        """Other names by language, each language with at least one."""
        if not self.is_a(value, dict, where, "aliases by language"):
            return
        for tag, aliases in value.items():
            place = join(where, tag)
            self.check_language(tag, place)
            self.check_list(aliases, {"of": {"is": "label"}, "at_least": 1}, place)


def check_thing(thing, model, words, kinds):
    """Every issue in the shape of one file."""
    shape_check = ShapeCheck(thing.path, model, words, kinds)
    kind_rule = {"is": "object", "fields": model["kinds"][thing.kind]["fields"]}
    shape_check.check(thing.data, kind_rule, "")
    return shape_check.issues
