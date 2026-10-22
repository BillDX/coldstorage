# RED (step 3): data integrity. The world graph and item placement
# must be self-consistent before any rules are built on top.
from collections import deque

from game import data


def test_every_exit_target_exists():
    for room in data.ROOMS.values():
        for direction, target in room.exits.items():
            if target is not None:
                assert target in data.ROOMS, f"{room.id} {direction} -> {target}"


def test_exits_are_symmetric():
    opposite = {"north": "south", "south": "north", "east": "west", "west": "east",
                "up": "down", "down": "up"}
    for room in data.ROOMS.values():
        for direction, target in room.exits.items():
            if target is None:
                continue
            other = data.ROOMS[target]
            assert other.exits.get(opposite[direction]) == room.id, (
                f"{room.id} {direction} -> {target}, but {target} has no {opposite[direction]} back"
            )


def test_map_is_fully_connected():
    start = "office"
    seen = {start}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for target in data.ROOMS[cur].exits.values():
            if target and target not in seen:
                seen.add(target)
                queue.append(target)
    assert seen == set(data.ROOMS), f"unreachable rooms: {set(data.ROOMS) - seen}"


def test_every_item_starts_in_a_real_room():
    for item in data.ITEMS.values():
        if item.initial_room is None:
            assert item.latent, f"{item.id} has no starting room but is not latent"
            continue
        assert item.initial_room in data.ROOMS, f"{item.id} starts in {item.initial_room}"


def test_required_items_exist_exactly_once():
    for req in data.REQUIRED_ITEMS:
        assert req in data.ITEMS, f"required item {req} missing"
    assert len(data.ITEMS) == len(set(data.ITEMS))


def test_sources_match_design():
    # The plan's single-source table, as a design contract.
    expected = {
        "flashlight": "security", "keyring": "office", "sandwich": "locker_room",
        "ducttape": "breakroom", "paperclip": "breakroom", "plunger": "bathroom",
        "screwdriver": "office", "fuse": "generator", "gascan": "generator",
        "coin": "lobby", "trophy": "office", "tape1": "breakroom",
        "tape2": "archive", "tape3": "office", "runbook": "office",
        "coffee": "breakroom",
    }
    for item, room in expected.items():
        assert item in data.ITEMS, f"missing {item}"
        assert data.ITEMS[item].initial_room == room, (
            f"{item} should start in {room}, not {data.ITEMS[item].initial_room}"
        )


def test_ghost_lives_in_server_room():
    assert data.GHOST_ROOM == "server"


def test_dark_rooms_match_design():
    dark = {r.id for r in data.ROOMS.values() if r.dark}
    assert dark == {"security", "archive", "breakroom", "bathroom", "substation", "generator"}


def test_room_count():
    assert len(data.ROOMS) == 11