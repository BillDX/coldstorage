# RED (step 6b): full playthrough + invariants. The game must be solvable
# end-to-end, and state must stay sane at every single turn.
from game import data
from game.engine import run
from game.game import GameState
from tests.solution import SOLUTION


def invariants(s: GameState) -> None:
    """Every item exists in exactly one place at all times."""
    where: dict[str, set] = {}
    for i in s.inventory:
        where.setdefault(i, set()).add("inventory")
    for i, r in s.item_loc.items():
        where.setdefault(i, set()).add(r)
    for i in s.backup_tapes:
        where.setdefault(i, set()).add("backup drive")
    for i, spots in where.items():
        assert len(spots) == 1, f"{i} in multiple places: {spots}"
    for i, it in data.ITEMS.items():
        if it.latent:
            continue  # may legitimately not exist yet
        if i in s.consumed:
            continue  # eaten, drank, or spent
        assert i in where, f"{i} lost from the world"


def test_full_playthrough_with_state():
    s = GameState()
    for cmd in SOLUTION:
        out = s.apply(cmd)
        assert out and out.strip(), f"empty response to: {cmd}"
        invariants(s)
    assert s.escaped
    assert s.door_open
    assert s.backup_done
    assert s.breaker_on
    assert "keycard" in s.inventory or s.keycard_given
    assert s.score >= 150


def test_full_playthrough_through_engine():
    transcript = run(SOLUTION)
    assert "COLD STORAGE" in transcript
    assert "THE END" in transcript
    assert "OBJECTIVE COMPLETE" in transcript


def test_every_objective_completes():
    s = GameState()
    for cmd in SOLUTION[:-1]:
        s.apply(cmd)
    s.apply("go north")
    # after escape the game answers everything with the same line, so check
    # the four objective flags directly.
    assert s.breaker_on          # 1: power
    assert s.backup_done         # 2: backup
    assert s.keycard_given       # 3: keycard
    assert s.door_open           # 4: door


def test_stuck_player_gets_guidance():
    """A confused player can always see what's left to do."""
    s = GameState()
    s.apply("take trophy")
    out = s.apply("score")
    assert "OBJECTIVES" in out
    assert "[x]" not in out
    out = s.apply("help")
    assert "commands" in out.lower()


def test_quit_before_escape_ends_gracefully():
    # spec changed: quit always ends the program (exit/leave only *suggest* it)
    s = GameState()
    out = s.apply("quit")
    assert s._force_quit
    assert "THE END" in out.upper()
    assert not s.escaped  # you left, but you never got out
