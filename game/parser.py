"""Command parser for COLD STORAGE.

Turns a raw line of text into a Command(verb, noun, noun2).
Supports classic adventure verbs, single-letter shortcuts, directions,
two-part "use X on/in/into/with Y" phrasing, and code entry.
"""
from __future__ import annotations

from dataclasses import dataclass

DIRECTIONS = {
    "n": "north", "north": "north",
    "s": "south", "south": "south",
    "e": "east", "east": "east",
    "w": "west", "west": "west",
    "u": "up", "up": "up",
    "d": "down", "down": "down",
}

# canonical verb -> set of surface forms
VERB_SYNONYMS = {
    "look": {"look", "l", "x", "examine", "ex", "inspect", "search"},
    "inventory": {"inventory", "i", "inv", "pack"},
    "take": {"take", "t", "get", "g", "pick", "grab", "steal", "loot"},
    "drop": {"drop", "d", "leave", "put down"},
    "use": {"use", "apply", "put", "insert", "swipe", "feed", "repair", "fix", "poke"},
    "read": {"read", "r", "cat", "open"},
    "go": {"go", "goto", "walk", "move", "waddle", "shuffle"},
    "open": {"open", "unseal", "unlock"},
    "close": {"close", "shut", "seal"},
    "pull": {"pull", "yank", "tug", "throw"},
    "push": {"push", "shove"},
    "shake": {"shake", "rattle", "agitate"},
    "start": {"start", "ignite", "fire"},
    "type": {"type", "enter", "key", "press", "type in"},
    "eat": {"eat", "munch", "devour", "consume", "ingest"},
    "drink": {"drink", "sip", "gulp"},
    "heat": {"heat", "warm"},
    "wave": {"wave", "greet", "salute"},
    "pray": {"pray", "pray to", "worship"},
    "exorcise": {"exorcise", "banish", "cast out"},
    "dance": {"dance", "twirl"},
    "scare": {"scare", "frighten"},
    "apologize": {"apologize", "apologise", "sorry"},
    "hire": {"hire", "employ", "contract"},
    "sue": {"sue", "litigate"},
    "kill": {"kill", "murder", "terminate"},
    "reboot": {"reboot", "restart", "reload"},
    "sudo": {"sudo"},
    "git": {"git"},
    "wait": {"wait", "w", "pause", "z"},
    "score": {"score", "points"},
    "quit": {"quit", "q", "exit"},
    "help": {"help", "h", "?"},
    "ask": {"ask", "talk", "tell", "say"},
}

VERBS = {surface: canon for canon, forms in VERB_SYNONYMS.items() for surface in forms}

TWO_WORD_VERBS = {
    "pick up": "take",
    "throw at": "use",
    "turn on": "start",
    "turn off": "use",
    "put on": "use",
}

SPLIT_ON = (" on ", " into ", " to ", " in ", " with ", " at ")


@dataclass
class Command:
    verb: str | None = None
    noun: str | None = None
    noun2: str | None = None

    def __str__(self) -> str:
        parts = [p for p in (self.verb, self.noun, self.noun2) if p]
        return " ".join(parts)


def _clean(text: str) -> str:
    text = text.strip().lower()
    text = " ".join(text.split())
    return text


def _resolve_verb(token: str) -> str | None:
    return VERBS.get(token)


def _split_noun2(noun: str) -> tuple[str, str | None]:
    """Split 'tape on hose' into ('tape', 'hose')."""
    for sep in SPLIT_ON:
        idx = noun.find(sep)
        if idx != -1:
            left = noun[:idx].strip()
            right = noun[idx + len(sep):].strip()
            if left:
                return left, (right or None)
    return noun, None


def parse(raw: str) -> Command:
    text = _clean(raw)
    if not text:
        return Command(verb=None)

    # Two-word verbs (check before single-token resolution).
    for two, canon in TWO_WORD_VERBS.items():
        if text.startswith(two):
            rest = text[len(two):].strip()
            noun, noun2 = _split_noun2(rest) if rest else (None, None)
            return Command(verb=canon, noun=noun, noun2=noun2)

    head, _, rest = text.partition(" ")
    rest = rest.strip()

    # Bare direction: "north" / "n" -> go north
    if not rest and head in DIRECTIONS:
        return Command(verb="go", noun=DIRECTIONS[head])

    canon = _resolve_verb(head)
    if canon is None:
        # Unknown verb: keep it raw so the game can pun on it.
        noun, noun2 = _split_noun2(rest) if rest else (None, None)
        return Command(verb=head, noun=noun, noun2=noun2)

    if canon == "go":
        if rest in DIRECTIONS:
            return Command(verb="go", noun=DIRECTIONS[rest])
        return Command(verb="go", noun=rest or None)

    noun, noun2 = _split_noun2(rest) if rest else (None, None)
    if noun:
        noun = noun.removeprefix("the ").strip() or None
    if noun2:
        noun2 = noun2.removeprefix("the ").strip() or None
    return Command(verb=canon, noun=noun, noun2=noun2)
