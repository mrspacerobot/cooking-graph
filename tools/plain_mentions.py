"""Finding a food named in plain words, by the names and aliases the graph gives it, in any language it knows.

A step must name the foods of its recipe lines through placeholders. To tell when it did not, every name and alias of
every ingredient and preparation is looked up in the text, the longest name first, so that 'olive oil' is read as the
olive oil it is and not as the oil in it. A plural is read as the one name: eggs is egg.
"""

import re

from tools import names

FOOD_KINDS = ("ingredient", "preparation")
WORD = re.compile(r"[a-z0-9]+")


def singular_forms(word):
    """The word, and what its singular may be when it ends like a plural."""
    forms = [word]
    if word.endswith("ies"):
        forms.append(word[:-3] + "y")
    if word.endswith("es"):
        forms.append(word[:-2])
    if word.endswith("s"):
        forms.append(word[:-1])
    return forms


class Vocabulary:
    """Every plain name of every food, and the foods that go by it."""

    def __init__(self, things):
        self.owners = {}
        for thing_id, thing in things.items():
            if thing.kind in FOOD_KINDS:
                for name in names.plain_names(thing.data):
                    self.owners.setdefault(name, set()).add(thing_id)
        self.longest = max([len(name.split(" ")) for name in self.owners] + [1])

    def owners_of(self, words):
        """The foods that go by these words, the last word read as singular too."""
        found = set()
        for last in singular_forms(words[-1]):
            found |= self.owners.get(" ".join(words[:-1] + [last]), set())
        return found

    def longest_at(self, words, start):
        """The longest name that starts at this word: how many words it takes, and the foods that go by it."""
        for count in range(min(self.longest, len(words) - start), 0, -1):
            owners = self.owners_of(words[start:start + count])
            if owners:
                return count, owners
        return 1, set()

    def foods_named_in(self, text):
        """The foods the text names in plain words: each as the words it used and the foods that go by them."""
        words = WORD.findall(names.plain(text))
        found = []
        position = 0
        while position < len(words):
            count, owners = self.longest_at(words, position)
            if owners:
                found.append((" ".join(words[position:position + count]), owners))
            position += count
        return found
