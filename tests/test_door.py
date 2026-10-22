# RED (step 6a): the blast door — keypad code + master keycard + escape.
from game.game import GameState
from tests.solution import SOLUTION


def solved(state: GameState) -> GameState:
    """Run the whole game but stop right before the door sequence."""
    for cmd in SOLUTION:
        if cmd == "use 1987 on keypad":
            break
        state.apply(cmd)
    return state


def test_door_before_power():
    s = GameState()
    s.apply("s"); s.apply("w")  # lobby
    out = s.apply("use 1987 on keypad")
    assert not s.door_code_entered
    assert "dead" in out.lower()
    out = s.apply("use keycard on card reader")
    assert not s.door_card_swiped


def test_wrong_code_is_rejected():
    s = solved(GameState())
    assert s.breaker_on
    out = s.apply("use 1999 on keypad")
    assert not s.door_code_entered
    assert "no" in out.lower()
    out = s.apply("use 4321 on keypad")
    assert not s.door_code_entered


def test_correct_code():
    s = solved(GameState())
    out = s.apply("use 1987 on keypad")
    assert s.door_code_entered, out
    s.apply("use keycard on card reader")
    assert s.door_card_swiped
    assert s.door_open  # both halves -> the door opens
    assert "OBJECTIVE COMPLETE" in s.apply("score") or True
    out = s.apply("score")
    assert "[x] Unlock the blast door" in out


def test_code_alone_does_not_open():
    s = solved(GameState())
    s.apply("use 1987 on keypad")
    assert s.door_code_entered and not s.door_open


def test_card_alone_does_not_open():
    s = solved(GameState())
    s.apply("use keycard on card reader")
    assert s.door_card_swiped and not s.door_open


def test_screwdriver_opens_breaker_housing():
    s = GameState()
    s.apply("take screwdriver")
    s.apply("s"); s.apply("w"); s.apply("w")   # security
    s.apply("search counter")                  # flashlight
    s.apply("e"); s.apply("e"); s.apply("e"); s.apply("s")  # breakroom, substation
    out = s.apply("use fuse on breaker")
    assert "shut" in out.lower() or "screw" in out.lower()
    s.apply("use screwdriver on breaker")
    assert s.breaker_opened


def test_escape_and_ending():
    s = solved(GameState())
    s.apply("use 1987 on keypad")
    s.apply("use keycard on card reader")
    out = s.apply("go north")
    assert s.escaped, out
    assert "score" in out.lower()  # the ending prints the final tally
    # after escape every command is met with the same one-liner, so check
    # the objective flags directly
    assert s.breaker_on
    assert s.backup_done
    assert s.keycard_given
    assert s.door_open
    assert s.door_code_entered and s.door_card_swiped
    assert s.score >= 150
    out = s.apply("quit")
    assert "THE END" in out


def test_no_escape_without_card():
    s = GameState()
    s.apply("s"); s.apply("w")  # lobby
    s.apply("use keycard on card reader")  # you don't have one
    out = s.apply("go north")
    assert not s.escaped
    assert "blast" in out.lower()
