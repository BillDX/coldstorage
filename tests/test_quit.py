"""Quit ends the game; exit/leave suggest it but keep you in the building."""
from game.engine import run
from game.game import GameState
from tests.test_door import solved


def test_quit_ends_the_program_mid_game():
    s = GameState()
    out = s.apply("quit")
    assert s._force_quit
    assert "THE END" in out.upper()


def test_q_ends_the_program_mid_game():
    s = GameState()
    s.apply("q")
    assert s._force_quit


def test_quit_still_works_after_escaping():
    s = solved(GameState())
    s.apply("use 1987 on keypad")
    s.apply("use keycard on card reader")
    s.apply("go north")
    assert s.escaped
    out = s.apply("quit")
    assert s._force_quit
    assert "THE END" in out.upper()


def test_exit_suggests_quit_but_keeps_you_in():
    s = GameState()
    out = s.apply("exit")
    assert "quit" in out.lower()
    assert not s._force_quit  # the building keeps you


def test_leave_suggests_quit_but_keeps_you_in():
    s = GameState()
    out = s.apply("leave")
    assert "quit" in out.lower()
    assert not s._force_quit


def test_quit_via_engine_returns_transcript():
    out = run(["quit"])
    assert "THE END" in out


def test_quit_shows_the_score():
    s = GameState()
    s.apply("take trophy")
    out = s.apply("quit")
    assert "score" in out.lower()