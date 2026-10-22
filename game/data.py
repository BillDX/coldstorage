"""World data for COLD STORAGE: rooms, items, and the design contract.

This module is pure data. All rules live in game/game.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    desc: str
    exits: dict = field(default_factory=dict)  # direction -> room_id | None
    dark: bool = False


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    initial_room: str | None  # None: not in the world until created (keycard, coffee)
    desc: str
    synonyms: tuple = ()
    fixed: bool = False   # cannot be picked up (furniture, machines, Gary)
    latent: bool = False  # not obtainable until something happens (coffee)


ROOMS: dict[str, Room] = {}


def room(id: str, name: str, desc: str, exits: dict | None = None, dark: bool = False) -> Room:
    r = Room(id=id, name=name, desc=desc, exits=exits or {}, dark=dark)
    ROOMS[id] = r
    return r


room(
    "office", "Your Office",
    "Your office. The fluorescent light flickers on and off like it is "
    "buffering. A sticky desk, a sagging chair, a laptop holding at 3% "
    "battery with zero mercy. The tool drawer hangs open. On the shelf a "
    "trophy glints — 'BEST EMPLOYEE, Q3 1987' — and it is suspiciously hollow.",
    exits={"south": "corridor", "west": "server"},
)
room(
    "corridor", "Corridor C4",
    "Corridor C4. Emergency exit signs glow the color of faint hope. The "
    "ceiling tiles are sweating. Somewhere above, a single wire hums one "
    "note and refuses, with great professionalism, to stop.",
    exits={"west": "lobby", "north": "office", "east": "breakroom", "south": "bathroom"},
)
room(
    "lobby", "The Lobby",
    "The lobby. A bench, a desk, and — across the room — the blast door: "
    "four inches of steel with a keypad and a card reader, both dark, both "
    "profoundly unimpressed by you.",
    exits={"east": "corridor", "west": "security", "south": "locker_room"},
)
room(
    "security", "The Security Desk",
    "The security desk. The chair is empty. The radio crackles: '...this "
    "is Doug, reporting all quiet...' It says all quiet again. It has been "
    "saying all quiet for a long time. Something under the counter has the "
    "shape and coldness of a flashlight.",
    dark=True,
    exits={"east": "lobby", "west": "archive"},
)
room(
    "archive", "The Tape Archive",
    "The tape archive. Racks of labeled tapes climb into the dark. One "
    "shelf is marked in red marker: DO NOT OPEN — BERNARD'S REGRETS. The "
    "marker is very smudged. Bernard clearly disagreed with this policy later.",
    dark=True,
    exits={"east": "security"},
)
room(
    "breakroom", "The Break Room",
    "The break room. A vending machine with its light out, a coffee machine "
    "on the verge of a breakdown, and a VCR playing nothing. The ceiling "
    "tiles are moving gently. It is probably Gary.",
    dark=True,
    exits={"west": "corridor", "south": "substation"},
)
room(
    "bathroom", "The Bathroom",
    "The bathroom. The tile is forty years out of date and extremely "
    "confident about it. A plunger leans against the tank at rest angle. "
    "The sink drips at a pace that suggests it is keeping time.",
    dark=True,
    exits={"north": "corridor"},
)
room(
    "server", "The Server Room",
    "The server room. The temperature drops twenty degrees. Your breath "
    "ghosts. Pale green UPS glow paints everything in the color of regret. "
    "A translucent figure in a short-sleeved dress shirt hovers over the "
    "racks. 'You're in my server room.'",
    exits={"east": "office"},
)
room(
    "substation", "The Substation",
    "The substation. A breaker panel dominates the wall like a monolith "
    "that has been interrupted from its brooding. The main breaker's "
    "housing is screwed shut. The dust on the fuse box is archaeological in scope.",
    dark=True,
    exits={"north": "breakroom", "south": "generator"},
)
room(
    "generator", "The Generator Room",
    "The generator room. A six-figure standby generator stands with its "
    "fuel hose separated from its fitting by one clean, confident bite "
    "mark. On top of the unit, a spare box holds exactly one fuse — "
    "jammed hard against the back, the way fuses do when they have "
    "somewhere to be and a grudge.",
    dark=True,
    exits={"north": "substation"},
)
room(
    "locker_room", "The Supply Alcove",
    "The supply alcove. A bank of lockers, all closed, except one: yours, "
    "hanging open with a lightness that is not your memory. It contains "
    "the sandwich. The sandwich has been waiting.",
    exits={"north": "lobby"},
)


ITEMS: dict[str, Item] = {}


def item(id: str, name: str, initial_room: str | None, desc: str,
         synonyms: tuple = (), fixed: bool = False, latent: bool = False) -> Item:
    i = Item(id=id, name=name, initial_room=initial_room, desc=desc,
             synonyms=synonyms, fixed=fixed, latent=latent)
    ITEMS[id] = i
    return i


# --- portable loot ---------------------------------------------------------
item("flashlight", "flashlight", "security",
     "A security flashlight. Its beam is strong enough to read meters and "
     "weak enough to apologize for. Still, in a building that has given up "
     "on electricity, it is the MVP.",
     synonyms=("torch", "lights", "flashlight", "light"))
item("keyring", "keyring", "office",
     "Your keyring. One key on it, one purpose. The key is confident in a way keys should not be.",
     synonyms=("keys", "key", "keyring"))
item("sandwich", "sandwich", "locker_room",
     "A turkey sandwich from 1987. It has achieved a state of matter that "
     "food science has names for but no words for. The label says 'DO NOT "
     "FEED THE RATS.' It says this in Bernard's handwriting.",
     synonyms=("lunch", "sandwich", "turkey"))
item("ducttape", "duct tape", "breakroom",
     "A roll of duct tape. The universal fix, the silver lining, the 'hold "
     "it together till Thursday.' It has opinions about your posture.",
     synonyms=("tape", "tape roll", "ducttape"))
item("paperclip", "paperclip", "breakroom",
     "A paperclip. It has never straightened a tape this hard.",
     synonyms=("clip", "paperclip"))
item("plunger", "plunger", "bathroom",
     "A plunger. The bathroom's champion, the siphon's nemesis, and — as "
     "it turns out — the finest surgical instrument this building has ever "
     "owned.",
     synonyms=("plunger", "suction", "clog doctor"))
item("screwdriver", "screwdriver", "office",
     "A flathead screwdriver. It is missing one screw's worth of confidence.",
     synonyms=("screwdriver", "driver", "flathead"))
item("fuse", "fuse", "generator",
     "A single fuse, fat and jammed. It hums. It is the only fuse in the "
     "building, which is either excellent engineering or a dare.",
     synonyms=("fuse", "breaker fuse"))
item("gascan", "gas can", "generator",
     "A gas can. Full, which for a can in a dead building is an act of faith.",
     synonyms=("gas", "fuel", "gascan", "gasoline"))
item("coin", "coin", "lobby",
     "A coin from 1986. It has been waiting for a machine to believe in it again.",
     synonyms=("coin", "quarter", "money"))
item("trophy", "trophy", "office",
     "'BEST EMPLOYEE, Q3 1987.' It is hollow, and when you tilt it, "
     "something rattles inside with a small, guilty sound. The award has "
     "secrets. The award always has secrets.",
     synonyms=("trophy", "award", "best employee"))
item("tape1", "backup tape, vol. 1", "breakroom",
     "A VHS labeled BERNARD'S FINAL BACKUP, VOL. 1. The tape is dark, thick, "
     "and heavier than VHS should be. It is the weight of a career.",
     synonyms=("tape 1", "vol 1", "volume 1", "tape1"))
item("tape2", "backup tape, vol. 2", "archive",
     "A VHS pulled from the REGRETS shelf: BERNARD'S FINAL BACKUP, VOL. 2. "
     "It is warm. You choose not to think about why.",
     synonyms=("tape 2", "vol 2", "volume 2", "tape2", "regrets"))
item("tape3", "backup tape, vol. 3", "office",
     "A VHS that falls out of the trophy like a confession: BERNARD'S FINAL "
     "BACKUP, VOL. 3. He hid his last night shift inside a hardware-store trophy.",
     synonyms=("tape 3", "vol 3", "volume 3", "tape3"))
item("keycard", "master keycard", None,
     "The MASTER keycard. It is cold in your hand and then, briefly, warm, "
     "the way a handshake is when you are not sure which of you is alive.",
     synonyms=("keycard", "card", "master keycard", "master card"), latent=True)
item("coffee", "coffee", "breakroom",
     "A coffee, dispensed by a machine that was dead for forty years and is "
     "now doing one perfect thing. It is, impossibly, the right temperature.",
     synonyms=("coffee", "latte", "espresso"), latent=True)

# --- runbook (read, not carried) -------------------------------------------
item("runbook", "laptop runbook", "office",
     "Your laptop at 3% battery, displaying the emergency runbook. The "
     "battery dies as you read it. The screen holds, one last act of "
     "loyalty, on the page that matters.",
     synonyms=("laptop", "runbook", "manual", "book"), fixed=True)

# --- fixed objects (the scenery you can argue with) -------------------------
item("hose", "fuel hose", "generator",
     "The generator's fuel hose, ending in a clean bite mark. The open end "
     "weeps a little. There is a fitting on the generator, and the two of "
     "them look like they used to be a couple.",
     synonyms=("hose", "fuel line", "fuel hose"), fixed=True)
item("fusebox", "fuse box", "generator",
     "The spare-parts box on top of the generator. One fuse inside, jammed "
     "against the back wall with the full commitment of a man who has "
     "decided not to be reached.",
     synonyms=("fuse box", "spare box", "box", "fusebox"), fixed=True)
item("vcr", "VCR", "breakroom",
     "A VCR, playing nothing, a tape wedged past the door. The mechanism "
     "has a small round button and one very stubborn hour.",
     synonyms=("vcr", "vhs player", "video", "vcr player"), fixed=True)
item("breaker", "main breaker", "substation",
     "The main breaker, in a housing screwed shut. Where its fuse should "
     "be, there is a socket, empty, and a sense of being personally insulted.",
     synonyms=("breaker", "main breaker", "panel", "fuse panel", "main panel"), fixed=True)
item("backupdrive", "backup drive", "server",
     "A backup drive bolted to the floor of the server room, three bays "
     "open, each labeled FINAL BACKUP. The drive is the only thing in the "
     "room that is not glowing.",
     synonyms=("drive", "backup drive", "backup", "recorder"), fixed=True)
item("mainframe", "mainframe terminal", "server",
     "The mainframe terminal. A CRT the size of a small opinion. When it "
     "lives, its cursor blinks with the calm of a man who has seen every "
     "outage and kept every note.",
     synonyms=("mainframe", "terminal", "crt", "computer"), fixed=True)
item("vending", "vending machine", "breakroom",
     "A vending machine. The glass glows dark and perfect, a shrine to a "
     "snack that will never be eaten standing up. The coffee button is "
     "labeled BERNARD'S RECIPE in a sticker that is not a sticker.",
     synonyms=("vending", "vending machine", "machine", "snack machine"), fixed=True)
item("gary", "Gary", "breakroom",
     "A rat the size of a toaster, sitting on the vending machine like a "
     "very opinionated paperweight. He has one front tooth that shines. He "
     "watches you. He is Gary. Gary was here before the outage and will be "
     "here after whatever this is.",
     synonyms=("gary", "rat", "toaster", "rodent"), fixed=True)
item("counter", "security counter", "security",
     "The security counter. Under it, past the legs and the dust, the shape "
     "and coldness of a flashlight — stashed by someone who planned to come back.",
     synonyms=("counter", "desk", "security desk", "security counter"), fixed=True)
item("keypad", "keypad", "lobby",
     "The blast door's keypad. Ten keys, a small display, and the faint "
     "certainty of a lock that has been waiting for a specific number.",
     synonyms=("keypad", "door keypad", "keyboard", "code pad"), fixed=True)
item("cardreader", "card reader", "lobby",
     "A card reader next to the keypad. Its window is dark and slightly "
     "judgmental, the way a turnstile looks at people without tickets.",
     synonyms=("card reader", "cardreader", "reader", "swipe"), fixed=True)
item("trophy_shelf", "shelf", "office",
     "The office shelf, holding the trophy and nothing else, which is its own kind of ceremony.",
     synonyms=("shelf",), fixed=True)

GHOST_ROOM = "server"
GHOST_NAME = "Bernard"
GHOST_DEATH_YEAR = 1987
DOOR_CODE = "1987"
BLAST_DOOR = ("lobby", "north")  # the sealed exit north of the lobby

# Items required to actually escape. (Sandwich, keyring, gascan, coin,
# coffee, trophy are beloved but not load-bearing.)
REQUIRED_ITEMS = (
    "flashlight", "ducttape", "plunger", "screwdriver",
    "tape1", "tape2", "tape3", "keycard",
)

OBJECTIVES = (
    "Restore generator power",
    "Complete Bernard's final backup",
    "Acquire the master keycard",
    "Unlock the blast door",
)