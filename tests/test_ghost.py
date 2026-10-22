# RED (step 5): Bernard, the final backup, and the master keycard.
from game.game import GameState


def power_on(state: GameState) -> None:
    """The documented power chain, from the office."""
    for c in ["s", "w", "w"]:            # security
        state.apply(c)
    state.apply("search counter")
    for c in ["e", "e", "e"]:            # breakroom
        state.apply(c)
    state.apply("take duct tape")
    for c in ["w", "s"]:                 # bathroom
        state.apply(c)
    state.apply("take plunger")
    for c in ["n", "e", "s", "s"]:       # generator
        state.apply(c)
    state.apply("use tape on hose")
    state.apply("use plunger on fuse box")
    state.apply("start generator")
    state.apply("go north")              # substation
    state.apply("use fuse on breaker")
    state.apply("pull breaker")
    assert state.breaker_on


def test_bernard_lives_in_server_room():
    s = GameState()
    s.apply("go west")
    out = s.apply("look")
    assert "bernard" in out.lower() or "translucent" in out.lower()
    out = s.apply("look at ghost")
    assert "bernard" in out.lower()


def test_ghost_gags_dont_break():
    s = GameState()
    s.apply("go west")
    for cmd in ["pray to ghost", "exorcise ghost", "dance with ghost",
                "scare ghost", "hire ghost", "sue ghost", "kill ghost",
                "reboot ghost", "sudo", "git blame ghost"]:
        out = s.apply(cmd)
        assert out.strip(), f"{cmd} produced no response"


def test_tape1_wedged_in_vcr():
    s = GameState()
    s.apply("go south"); s.apply("go west")   # lobby
    s.apply("go west")                         # security
    s.apply("search counter")                  # flashlight
    s.apply("go east"); s.apply("go east"); s.apply("go east")  # breakroom
    out = s.apply("use paperclip on vcr")
    assert "tape1" not in s.inventory
    s.apply("take paperclip")
    out = s.apply("use paperclip on vcr")
    assert "tape1" in s.inventory, out
    assert s.score >= 10


def test_tape3_hidden_in_trophy():
    s = GameState()
    s.apply("take trophy")
    out = s.apply("shake trophy")
    assert "tape3" not in s.inventory       # first shake: it rattles
    out = s.apply("shake trophy")
    assert "tape3" not in s.inventory or "vol. 3" in out.lower(), out
    # if it just fell out, take it
    if "tape3" not in s.inventory:
        s.apply("take tape 3")
        assert "tape3" in s.inventory


def test_tape2_in_archive_needs_light():
    s = GameState()
    s.apply("go south"); s.apply("go west"); s.apply("go west"); s.apply("go west")  # archive (dark)
    s.apply("take tape 2")
    assert "tape2" not in s.inventory
    s.apply("go east")           # security
    s.apply("search counter")    # flashlight
    s.apply("go west")           # archive, lit
    s.apply("take tape 2")
    assert "tape2" in s.inventory


def test_drive_is_dead_without_power():
    s = GameState()
    s.apply("take trophy"); s.apply("shake trophy"); s.apply("shake trophy")
    s.apply("take tape 3")
    s.apply("go west")           # server
    out = s.apply("use tape 3 on drive")
    assert not s.backup_done
    assert "dead" in out.lower() or "power" in out.lower()


def test_full_backup_and_keycard():
    s = GameState()
    power_on(s)  # ends in the generator room
    s.apply("go north")                      # substation
    s.apply("go north")                      # breakroom
    s.apply("take paperclip")
    s.apply("use paperclip on vcr")          # tape1
    s.apply("go west"); s.apply("go west")   # corridor, lobby
    s.apply("go west"); s.apply("go west")   # security, archive
    s.apply("take tape 2")
    s.apply("go east"); s.apply("go east"); s.apply("go east")  # security, lobby, corridor
    s.apply("go north")                      # office
    s.apply("take trophy")
    s.apply("shake trophy"); s.apply("shake trophy")
    s.apply("take tape 3")
    s.apply("go west")                       # server
    assert {"tape1", "tape2", "tape3"} <= s.inventory
    out = s.apply("use tape 1 on drive")
    assert "tape1" in s.backup_tapes, out
    s.apply("use tape 2 on drive")
    out = s.apply("use tape 3 on drive")
    assert s.backup_done, out
    assert s.ghost_peaceful, out
    assert "keycard" in s.inventory, out     # Bernard hands it over
    assert "OBJECTIVE COMPLETE" in out or "objective" in out.lower()


def test_bernard_reveals_code_when_peaceful():
    s = GameState()
    power_on(s)  # ends in the generator room
    s.apply("go north")                      # substation
    s.apply("go north")                      # breakroom
    s.apply("take paperclip")
    s.apply("use paperclip on vcr")
    s.apply("go west"); s.apply("go west")   # corridor, lobby
    s.apply("go west"); s.apply("go west")   # security, archive
    s.apply("take tape 2")
    s.apply("go east"); s.apply("go east"); s.apply("go east"); s.apply("go north")  # ... corridor, office
    s.apply("take trophy"); s.apply("shake trophy"); s.apply("shake trophy")
    s.apply("take tape 3")
    s.apply("go west")  # server
    s.apply("use tape 1 on drive"); s.apply("use tape 2 on drive")
    out = s.apply("ask ghost about the door code")
    assert "1987" not in out.lower()         # not yet done
    s.apply("use tape 3 on drive")
    out = s.apply("ask ghost about the door code")
    assert "1987" in out.lower(), out


def test_ghost_blocks_nothing_mechanically_but_keeps_keycard():
    s = GameState()
    power_on(s)
    s.apply("go west")  # server
    assert "keycard" not in s.inventory
    s.apply("take keycard")   # it is not in the room yet
    assert "keycard" not in s.inventory
