"""The canonical solution as a command script (the 'speedwalk' of ghosts).

Used by the door tests and the full playthrough test. It must start in the
office and end outside the building.
"""

SOLUTION = [
    # --- office: trophy, tools, and the runbook ----------------------------
    "take trophy",
    "shake trophy",
    "shake trophy",
    "take tape 3",
    "take screwdriver",
    # --- lobby + security: coin and the flashlight --------------------------
    "s", "w",
    "take coin",
    "w",
    "search counter",
    # --- breakroom: tape, clip, and vol. 1 out of the VCR -------------------
    "e", "e", "e",
    "take duct tape",
    "take paperclip",
    "use paperclip on vcr",
    # --- archive: vol. 2 (dark room, flashlight) ----------------------------
    "w", "w", "w", "w",
    "take tape 2",
    # --- back to the office, read the runbook -------------------------------
    "e", "e", "e", "n",
    "read runbook",
    "s", "s",
    "take plunger",
    "n", "n",
    # --- the server: the machine is still dead, but ask ----------------------
    "w",
    "read mainframe",
    "e", "s", "e", "s",    # office, corridor, breakroom, substation
    "use screwdriver on breaker",
    "s",                    # generator
    "use tape on hose",
    "use plunger on fuse box",
    "start generator",
    "n",                    # substation
    "use fuse on breaker",
    "pull breaker",
    # --- a small mercy: the vending machine works now ------------------------
    "n",                    # breakroom
    "use coin on vending",
    "drink coffee",
    # --- back up to the server: finish the backup ----------------------------
    "w", "n",               # corridor, office
    "w",                    # server
    "use tape 1 on drive",
    "use tape 2 on drive",
    "ask ghost about the door code",
    "use tape 3 on drive",  # backup done -> keycard
    # --- the lobby: the door -------------------------------------------------
    "e", "s", "w",
    "use 1987 on keypad",
    "use keycard on card reader",
    "go north",
    "quit",
]
