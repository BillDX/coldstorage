# RED (step 4): game core + the power chain.
# The escape's critical path part 1: hose -> fuse -> generator -> breaker.
from game.game import GameState


def g(*cmds):
    state = GameState()
    for c in cmds:
        state.apply(c)
    return state


def to(s, room_id):
    """Walk the map to a room (deterministic, no puzzles involved in walking)."""
    paths = {
        "office": [],
        "corridor": ["s"],
        "lobby": ["s", "w"],
        "security": ["s", "w", "w"],
        "archive": ["s", "w", "w", "w"],
        "locker_room": ["s", "w", "s"],
        "breakroom": ["s", "e"],
        "bathroom": ["s", "s"],
        "server": ["w"],
        "substation": ["s", "e", "s"],
        "generator": ["s", "e", "s", "s"],
    }
    for step in paths[room_id]:
        s.apply(step)
    return s


def test_start_in_office():
    s = g()
    out = s.apply("look")
    assert "office" in out.lower()
    assert s.room == "office"


def test_movement():
    s = to(g(), "lobby")
    out = s.apply("look")
    assert "lobby" in out.lower()
    s.apply("go east")
    assert s.room == "corridor"


def test_blast_door_is_sealed():
    s = to(g(), "lobby")
    out = s.apply("go north")
    assert s.room == "lobby"  # still here
    assert "blast" in out.lower()


def test_dark_room_hides_items():
    s = to(g(), "archive")  # dark, no light yet
    out = s.apply("look")
    assert "dark" in out.lower()
    assert "tape" not in out.lower()  # items hidden in the dark
    out = s.apply("take tape 2")
    assert "dark" in out.lower()
    assert "tape2" not in s.inventory


def test_flashlight_groped_in_security():
    s = to(g(), "security")
    out = s.apply("search counter")
    assert "flashlight" in out.lower()
    assert "flashlight" in s.inventory


def test_flashlight_reveals_items():
    s = to(g(), "security")
    s.apply("search counter")
    s.apply("go west")  # archive, now lit by flashlight
    out = s.apply("look")
    assert "tape" in out.lower()  # vol 2 visible
    assert "tape2" not in s.inventory


def test_take_and_drop():
    s = to(g(), "office")
    s.apply("take keyring")
    assert "keyring" in s.inventory
    s.apply("drop keyring")
    assert "keyring" not in s.inventory
    assert "keyring" in s.item_loc


def test_hose_requires_tape():
    s = to(g(), "generator")
    # the generator room is dark and we have no light: interactions are blocked
    out = s.apply("use tape on hose")
    assert not s.hose_fixed
    assert "dark" in out.lower()
    # even with a flashlight, no tape means no fix
    s2 = to(g(), "security")
    s2.apply("search counter")
    s2.apply("go east"); s2.apply("go east")  # lobby, corridor
    s2.apply("go east"); s2.apply("go south")  # breakroom, substation
    s2.apply("go south")  # generator
    out = s2.apply("use tape on hose")
    assert not s2.hose_fixed
    assert "tape" in out.lower()  # tells us what it needs


def test_full_power_chain():
    s = to(g(), "breakroom")
    s.apply("take duct tape")  # needs light... flashlight first
    assert "ducttape" not in s.inventory  # it's dark
    # get the light
    s.apply("go west")        # corridor
    s.apply("go west")        # lobby
    s.apply("go west")        # security
    s.apply("search counter")
    assert "flashlight" in s.inventory
    s.apply("go east")        # lobby
    s.apply("go east")        # corridor
    s.apply("go east")        # breakroom
    s.apply("take duct tape")
    assert "ducttape" in s.inventory
    # plunger
    s.apply("go west")        # corridor
    s.apply("go south")       # bathroom
    s.apply("take plunger")
    assert "plunger" in s.inventory
    s.apply("go north")       # corridor
    s.apply("go east")        # breakroom
    s.apply("go south")       # substation
    s.apply("go south")       # generator
    # fix hose
    out = s.apply("use tape on hose")
    assert s.hose_fixed, out
    # free the fuse
    out = s.apply("use plunger on fuse box")
    assert "fuse" in s.inventory, out
    # start the generator
    out = s.apply("start generator")
    assert s.generator_running, out
    assert not s.breaker_on, out
    # breaker
    s.apply("go north")  # substation
    out = s.apply("pull breaker")
    assert not s.breaker_on, out  # no fuse yet
    s.apply("use fuse on breaker")
    assert "fuse" not in s.inventory
    out = s.apply("pull breaker")
    assert s.breaker_on, out
    assert "power" in out.lower() or "light" in out.lower()


def test_power_lights_dark_rooms():
    s = GameState()
    for c in ["s", "w", "w"]:  # security
        s.apply(c)
    s.apply("search counter")
    for c in ["e", "e", "e"]:  # breakroom
        s.apply(c)
    s.apply("take duct tape")
    assert "ducttape" in s.inventory  # flashlight lit the break room
    for c in ["w", "s"]:  # bathroom
        s.apply(c)
    s.apply("take plunger")
    for c in ["n", "e", "s", "s"]:  # generator
        s.apply(c)
    s.apply("use tape on hose")
    s.apply("use plunger on fuse box")
    s.apply("start generator")
    s.apply("go north")  # substation
    s.apply("use fuse on breaker")
    s.apply("pull breaker")
    assert s.breaker_on
    out = s.apply("look")  # substation is dark by design
    assert "dark" not in out.lower()


def test_score_and_status():
    s = g()
    out = s.apply("score")
    assert "[ ]" in out
    assert "Restore generator power" in out
    assert "0" in out  # score zero


def test_inventory_list():
    s = g("take keyring", "take screwdriver")
    out = s.apply("inventory")
    assert "keyring" in out.lower()
    assert "screwdriver" in out.lower()


def test_unknown_verb_is_a_pun_not_a_crash():
    s = g()
    out = s.apply("frobnicate the hose")
    assert out  # some witty refusal
    out = s.apply("sudo")
    assert "1987" in out or "root" in out.lower()