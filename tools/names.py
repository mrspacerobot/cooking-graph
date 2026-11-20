"""Names in plain form, so that two spellings of one name are seen as one."""

import re
import unicodedata

# Letters that are two letters joined. Unicode does not split them by itself.
JOINED_LETTERS = {"œ": "oe", "Œ": "oe", "æ": "ae", "Æ": "ae"}
NOT_A_LETTER_OR_DIGIT = re.compile(r"[^a-z0-9]+")


def plain(word):
    """Fold Latin spellings and preserve other scripts, with punctuation read as spaces."""
    if not word.isascii() and not is_latin(word):
        normalized = unicodedata.normalize("NFKC", word.casefold())
        letters = [letter if unicodedata.category(letter)[0] in "LMN" else " " for letter in normalized]
        return " ".join("".join(letters).split())
    for joined, apart in JOINED_LETTERS.items():
        word = word.replace(joined, apart)
    decomposed = unicodedata.normalize("NFKD", word)
    letters = [letter for letter in decomposed if not unicodedata.combining(letter)]
    lowered = "".join(letters).lower()
    return NOT_A_LETTER_OR_DIGIT.sub(" ", lowered).strip()


def is_latin(text):
    """True when every letter of the text is in the Latin script."""
    for letter in text:
        if letter.isalpha() and "LATIN" not in unicodedata.name(letter, ""):
            return False
    return True


def all_names(data):
    """Every name and alias a thing goes by, in every language."""
    found = list(data.get("names", {}).values())
    for aliases in data.get("aliases", {}).values():
        found.extend(aliases)
    return found


def plain_names(data):
    return {plain(name) for name in all_names(data)}
