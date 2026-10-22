"""The text of a recipe step: read it, and render it for the foods a cook really uses.

A step never names a food of its recipe lines in plain words. It writes a placeholder, `{part}`, keyed by the
`part` the line fills, so that code can put the name of a swapped-in food in its place. Text that belongs to an
optional part sits in a clause, `[part: text]`, so that code can drop it when the part is left out. The format is
in `docs/recipe-steps.md`. This file is the reference for it: the checker reads text with `parse`, and the
serving vectors are written with `render`, so a server that renders the same way is proven by those vectors.
"""

import re
from collections import namedtuple

# Words that keep their capital inside a sentence, such as Dijon in Dijon mustard. A name whose first word is not
# here is written with a small first letter when it stands inside a sentence.
PROPER_NAME_WORDS = ("Arborio", "Basmati", "Dijon", "Gruyère", "Kashmiri", "Marsala", "Parmesan")

# `{part}` or `{part.slug}`; `[part: ` opens a clause, `]` closes it; any other bracket is a mistake.
TOKEN = re.compile(r"\{(?P<body>[^{}\[\]]*)\}|\[(?P<part>[a-z0-9-]+): |(?P<close>\])|(?P<stray>[{}\[])")
MENTION_BODY = re.compile(r"^(?P<part>[a-z0-9-]+)(?:\.(?P<slug>[a-z0-9-]+))?(?P<plural>:plural)?$")
SENTENCE_START = re.compile(r"(^|[.!?]\s+)$")
ARTICLE_BEFORE = re.compile(r"(^|[^A-Za-z])(?P<article>[Aa]n?)(?P<space>\s+)$")
VOWELS = "aeiouAEIOU"

# `slug` is None when the part holds one food and the part alone names it. `plural` asks for the plural of its name.
Mention = namedtuple("Mention", ["part", "slug", "plural"])


class Clause:
    """Text that holds only when its part is kept: the pieces are text and mentions, never another clause."""

    def __init__(self, part):
        self.part = part
        self.pieces = []

    def __repr__(self):
        return "Clause(%r, %r)" % (self.part, self.pieces)


class Reading:
    """Reads a text piece by piece and collects what is wrong with it."""

    def __init__(self):
        self.pieces = []
        self.problems = []
        self.clause = None

    def inside(self):
        if self.clause is None:
            return self.pieces
        return self.clause.pieces

    def add_text(self, text):
        if text:
            self.inside().append(text)

    def add_mention(self, body):
        found = MENTION_BODY.match(body)
        if found is None:
            self.problems.append("'{%s}' is no placeholder: write {part}, {part.ingredient} or either with :plural" % body)
            return
        self.inside().append(Mention(found.group("part"), found.group("slug"), found.group("plural") is not None))

    def open_clause(self, part):
        if self.clause is not None:
            self.problems.append("a clause '[%s: ' starts inside the clause of '%s'" % (part, self.clause.part))
            return
        self.clause = Clause(part)
        self.pieces.append(self.clause)

    def close_clause(self):
        if self.clause is None:
            self.problems.append("a ']' closes no clause")
            return
        self.clause = None

    def take(self, token):
        if token.group("body") is not None:
            self.add_mention(token.group("body"))
        elif token.group("part") is not None:
            self.open_clause(token.group("part"))
        elif token.group("close") is not None:
            self.close_clause()
        else:
            self.problems.append("a stray '%s'" % token.group("stray"))

    def finish(self):
        if self.clause is not None:
            self.problems.append("the clause of '%s' is never closed" % self.clause.part)
        return self.pieces, self.problems


def parse(text):
    """The pieces of a text (strings, mentions, clauses) and the problems found in how it is written."""
    reading = Reading()
    position = 0
    for token in TOKEN.finditer(text):
        reading.add_text(text[position:token.start()])
        reading.take(token)
        position = token.end()
    reading.add_text(text[position:])
    return reading.finish()


def mentions_of(pieces):
    """Every mention in the pieces, with the part of the clause it sits in, or None outside any clause."""
    found = []
    for piece in pieces:
        if isinstance(piece, Mention):
            found.append((piece, None))
        elif isinstance(piece, Clause):
            found.extend((inner, piece.part) for inner in piece.pieces if isinstance(inner, Mention))
    return found


def plain_pieces(pieces):
    """The stretches of ordinary words, each apart, so that no phrase is read across a placeholder."""
    found = []
    for piece in pieces:
        if isinstance(piece, str):
            found.append(piece)
        elif isinstance(piece, Clause):
            found.extend(inner for inner in piece.pieces if isinstance(inner, str))
    return found


def clauses_of(pieces):
    return [piece for piece in pieces if isinstance(piece, Clause)]


def spoken_name(english, proper_name_words):
    """A name as it stands inside a sentence: the first letter small, unless the first word is a proper name."""
    first_word = english.split(" ")[0]
    if first_word in proper_name_words:
        return english
    return english[:1].lower() + english[1:]


def at_sentence_start(written):
    return SENTENCE_START.search(written) is not None


class Rendering:
    """Writes the text of a step. `name_of(mention)` gives the English name of the food in use for the mention."""

    def __init__(self, name_of, left_out, proper_name_words):
        self.name_of = name_of
        self.left_out = set(left_out)
        self.proper_name_words = proper_name_words
        self.written = ""

    def agree_article(self, name):
        """'a' or 'an' written before a placeholder is chosen again from the first letter of the name in use."""
        found = ARTICLE_BEFORE.search(self.written)
        if found is None:
            return
        article = "an" if name[:1] in VOWELS else "a"
        if found.group("article")[0] == "A":
            article = article.capitalize()
        self.written = self.written[:found.start("article")] + article + found.group("space")

    def add_mention(self, mention):
        name = self.name_of(mention)
        if at_sentence_start(self.written):
            name = name[:1].upper() + name[1:]
        else:
            name = spoken_name(name, self.proper_name_words)
        self.agree_article(name)
        self.written += name

    def add_clause(self, clause):
        if clause.part in self.left_out:
            self.written = self.written.rstrip()
            return
        self.add_pieces(clause.pieces)

    def add_pieces(self, pieces):
        for piece in pieces:
            if isinstance(piece, str):
                self.written += piece
            elif isinstance(piece, Mention):
                self.add_mention(piece)
            else:
                self.add_clause(piece)


def render(pieces, name_of, left_out, proper_name_words):
    """The text a cook reads. An empty text means the whole step goes, with its time and its safety points."""
    rendering = Rendering(name_of, left_out, proper_name_words)
    rendering.add_pieces(pieces)
    return rendering.written.strip()
