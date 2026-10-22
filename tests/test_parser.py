# RED (step 2): command parser. Fail first, then implement game/parser.py green.
from game.parser import Command, parse


def test_empty_command():
    c = parse("")
    assert c.verb is None


def test_look():
    assert parse("look").verb == "look"
    assert parse("l").verb == "look"
    assert parse("x").verb == "look"


def test_go_directions():
    assert parse("north").verb == "go" and parse("north").noun == "north"
    assert parse("n").noun == "north"
    assert parse("go east").noun == "east"
    assert parse("w").noun == "west"
    assert parse("go north").noun == "north"
    assert parse("e").noun == "east"


def test_take_and_inventories():
    assert parse("take trophy").verb == "take" and parse("take trophy").noun == "trophy"
    assert parse("t trophy").verb == "take"
    assert parse("get tape 1").noun == "tape 1"
    assert parse("inventory").verb == "inventory"
    assert parse("i").verb == "inventory"


def test_two_part_uses():
    c = parse("use tape on hose")
    assert c.verb == "use" and c.noun == "tape" and c.noun2 == "hose"
    c = parse("put fuse in breaker")
    assert c.verb == "use" and c.noun == "fuse" and c.noun2 == "breaker"
    c = parse("insert tape 1 into drive")
    assert c.verb == "use" and c.noun == "tape 1" and c.noun2 == "drive"
    c = parse("shake trophy")
    assert c.verb == "shake" and c.noun == "trophy"
    c = parse("feed sandwich to gary")
    assert c.verb == "use" and c.noun == "sandwich" and c.noun2 == "gary"
    c = parse("turn on light")
    assert c.verb == "start" and c.noun == "light"


def test_code_entry_on_keypad():
    c = parse("use 1987 on keypad")
    assert c.verb == "use" and c.noun == "1987" and c.noun2 == "keypad"
    c = parse("type 1987")
    assert c.verb == "type" and c.noun == "1987"
    c = parse("enter 1987")
    assert c.verb == "type" and c.noun == "1987"


def test_read():
    assert parse("read runbook").verb == "read" and parse("read runbook").noun == "runbook"
    assert parse("r runbook").verb == "read"


def test_readme_and_quitting():
    assert parse("quit").verb == "quit"
    assert parse("q").verb == "quit"
    assert parse("help").verb == "help"
    assert parse("h").verb == "help"


def test_unknown_verb():
    c = parse("frobnicate the hose")
    assert c.verb == "frobnicate"


def test_verb_after_go_is_direction_not_verb():
    # "go north" must not parse as verb=go noun=None then "north" as verb
    c = parse("go north")
    assert c.verb == "go" and c.noun == "north"
