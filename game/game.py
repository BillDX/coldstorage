"""COLD STORAGE — game state and rules.

All game logic lives here as a pure function of GameState so the whole
thing is scriptable and testable. The interactive loop lives in engine.py.
"""
from __future__ import annotations

from . import data as d
from .parser import parse

# --------------------------------------------------------------------------
# alias table: every surface name -> item id, plus the ghost
# --------------------------------------------------------------------------
ALIASES: dict[str, str] = {}
for _id, _it in d.ITEMS.items():
    ALIASES[_id.lower()] = _id
    ALIASES[_it.name.lower()] = _id
    for _syn in _it.synonyms:
        ALIASES[_syn] = _id
for _g in ("ghost", "bernard", "figure", "translucent figure", "him",
           "sysadmin", "night shift", "the dead"):
    ALIASES[_g] = "ghost"


class GameState:
    def __init__(self) -> None:
        self.room = "office"
        self.inventory: set[str] = set()
        self.item_loc: dict[str, str] = {}
        for iid, it in d.ITEMS.items():
            if not it.latent and it.initial_room is not None:
                self.item_loc[iid] = it.initial_room

        # --- the escape state machine --------------------------------------
        self.hose_fixed = False
        self.fuse_taken = False
        self.fuse_in_breaker = False
        self.generator_running = False
        self.breaker_on = False          # building power

        self.tape3_in_trophy = True
        self.backup_tapes: set[str] = set()
        self.backup_done = False
        self.ghost_peaceful = False
        self.keycard_given = False

        self.door_code_entered = False
        self.door_card_swiped = False
        self.door_open = False
        self.escaped = False

        self.gary_fed = False
        self.vending_tried = False
        self.sandwich_eaten = False
        self.trophy_shakes = 0

        self.score = 0
        self.turn = 0
        self._force_quit = False
        self.seen: set[str] = set()      # one-shot hints & gags

    # ------------------------------------------------------------------ util
    def item(self, alias: str) -> str | None:
        return ALIASES.get(alias.lower().strip())

    def is_lit(self, room_id: str | None = None) -> bool:
        r = d.ROOMS[room_id or self.room]
        if self.breaker_on or not r.dark:
            return True
        return "flashlight" in self.inventory

    def resolve(self, raw: str | None) -> str | None:
        if not raw:
            return None
        return self.item(raw)

    def add_score(self, pts: int) -> None:
        self.score += pts

    # ------------------------------------------------------------- rendering
    def room_text(self) -> str:
        r = d.ROOMS[self.room]
        if not self.is_lit():
            return (
                "It's pitch dark. You are in a room you know by reputation. "
                "(Light or power would help.)"
            )
        lines = [r.name, "", r.desc]
        if self.room == "server" and self.ghost_peaceful:
            lines.append("The cold is gone. Where Bernard stood there is a "
                         "faint warm glow, and the racks hum in a major key.")
        visible = [
            d.ITEMS[i].name for i, loc in self.item_loc.items()
            if loc == self.room and not (i == "tape3" and self.tape3_in_trophy)
        ]
        if visible:
            lines += ["", "You see here: " + ", ".join(visible) + "."]
        exits = [x for x in r.exits if r.exits[x] is not None]
        extra = " (north: the blast door, sealed)" if self.room == "lobby" else ""
        lines.append("")
        lines.append("Exits: " + (" ".join(exits) or "none") + extra)
        return "\n".join(lines)

    # -------------------------------------------------------------- apply()
    HANDLERS = {
        "go": "_go", "look": "_look", "inventory": "_inventory",
        "take": "_take", "drop": "_drop", "use": "_use", "read": "_read",
        "start": "_start", "pull": "_pull", "shake": "_shake",
        "score": "_score", "help": "_help", "quit": "_quit",
        "eat": "_eat", "drink": "_drink", "heat": "_heat",
        "wait": "_wait", "open": "_open", "close": "_close", "ask": "_ask",
    }

    def apply(self, raw: str) -> str:
        self.turn += 1
        if self.escaped:
            return ("You are outside, which is where people go. The door "
                    "behind you is doing its one good thing: holding. "
                    "(Type 'quit' to end the game.)")
        c = parse(raw)
        if c.verb is None:
            return "(Type 'help' for a list of commands.)"
        handler = self.HANDLERS.get(c.verb)
        if handler is None:
            return self._gag(c)
        return getattr(self, handler)(c)

    # --------------------------------------------------------------- verbs
    def _go(self, c) -> str:
        r = d.ROOMS[self.room]
        target = r.exits.get(c.noun or "")
        if c.noun == "north" and self.room == "lobby":
            return self._blast_door_text()
        if target is None:
            return f"You cannot go {c.noun or 'that way'}."
        self.room = target
        return self.room_text()

    def _blast_door_text(self) -> str:
        if self.door_open:
            return ("You step through the blast door and into daylight. "
                    "\n\n" + self._ending())
        bits = ["The blast door does not move. Four inches of steel have "
                "very good bones."]
        if not self.breaker_on:
            bits.append("The keypad and card reader are dark.")
        return " ".join(bits)

    def _ending(self) -> str:  # filled in by the door step; placeholder safe
        return "You made it out."

    def _look(self, c) -> str:
        if c.noun is None:
            return self.room_text()
        # groping the security counter in the dark
        if self.resolve(c.noun) == "counter" and self.room == "security":
            if ("flashlight" in self.item_loc
                    and self.item_loc["flashlight"] == "security"
                    and "flashlight" not in self.inventory):
                self.inventory.add("flashlight")
                return ("You kneel and feel under the counter, fingers first, "
                        "dignity later. Cold metal. Yes. The flashlight. "
                        "Someone planned to come back, and you are that someone now.")
            return "The counter is dust and old stickers and one chair that " \
                   "has opinions."
        iid = self.resolve(c.noun)
        if iid == "ghost":
            return self._ghost_look()
        if iid is None:
            return f"You don't see any {c.noun} here."
        if not self.is_lit():
            return "It's dark. Looking at things requires things to be visible."
        if iid in self.inventory or self.item_loc.get(iid) == self.room:
            return d.ITEMS[iid].desc
        return f"There is no {d.ITEMS[iid].name} here."

    def _inventory(self, c) -> str:
        if not self.inventory:
            return "You are carrying: nothing, except confidence."
        names = [d.ITEMS[i].name for i in sorted(self.inventory)]
        return "You are carrying: " + ", ".join(names) + "."

    def _take(self, c) -> str:
        names = []
        if c.noun == "all":
            cands = [i for i, loc in self.item_loc.items()
                     if loc == self.room and not d.ITEMS[i].fixed
                     and i not in self.inventory
                     and not (i == "tape3" and self.tape3_in_trophy)]
            if not cands:
                return "You take all of it. It is nothing. It was always going to be nothing."
            if not self.is_lit():
                return "It's dark. Taking everything is a bold idea with a bad address."
            for i in cands:
                self.inventory.add(i)
                del self.item_loc[i]
                names.append(d.ITEMS[i].name)
            return "You take " + ", ".join(names) + "."
        iid = self.resolve(c.noun)
        if iid is None:
            return f"There is no {c.noun} here."
        if iid in self.inventory:
            return f"You already have the {d.ITEMS[iid].name}."
        if iid == "ghost":
            return ("You reach for the ghost. Your hand goes through him "
                    "like a rumor. He is not amused, which is impressive, "
                    "given he is dead.")
        it = d.ITEMS[iid]
        if it.fixed:
            if iid == "gary":
                return "Gary does not leave. Gary is load-bearing."
            return f"The {it.name} is not going anywhere. It has commitment issues."
        if self.item_loc.get(iid) != self.room:
            return f"There is no {it.name} here."
        if not self.is_lit():
            return "It's dark. You could be carrying the {name}, but the " \
                   "{name} would need to know you were here.".format(name=it.name)
        self.inventory.add(iid)
        del self.item_loc[iid]
        return f"You take the {it.name}."

    def _drop(self, c) -> str:
        iid = self.resolve(c.noun)
        if iid is None or iid not in self.inventory:
            return f"You aren't carrying any {c.noun or 'thing'}."
        self.inventory.discard(iid)
        self.item_loc[iid] = self.room
        return f"You drop the {d.ITEMS[iid].name}."

    # ------------------------------------------------------------------ use
    def _use(self, c) -> str:
        a = self.resolve(c.noun)
        b = self.resolve(c.noun2) if c.noun2 else None
        if a and b:
            pair = (a, b)
            if (a, b) in (("ducttape", "hose"),):
                return self._tape_hose()
            if (a, b) in (("plunger", "fusebox"),):
                return self._plunger_fusebox()
            if (a, b) in (("fuse", "breaker"),):
                return self._fuse_breaker()
            if a in ("tape1", "tape2", "tape3") and b == "backupdrive":
                return self._insert_tape(a)
            if (a, b) in (("paperclip", "vcr"),):
                return self._vcr_eject()
            if b == "vending" or (a, b) in (("coin", "vending"),):
                return self._vending()
            if a == "gascan" and b is None:
                return "The gas can is full. This is, in a dead building, a small miracle."
            if a == "flashlight":
                if b == "ghost":
                    return ("You shine the flashlight at the ghost. The beam "
                            "passes through him and hits a wall. He says "
                            "'I've had worse lighting.'" )
                return f"You shine the light on the {d.ITEMS[b].name if b else 'room'}. " \
                       f"It is a {d.ITEMS[b].name if b else 'room'}. Impressive lighting."
            if a == "sandwich" and b == "gary":
                return self._feed_gary()
            if b and not self.is_lit():
                return "It's too dark to fiddle with things."
            return f"The {d.ITEMS[a].name} has no interest in the " \
                   f"{d.ITEMS[b].name if b else 'situation'}."
        if a is None and c.noun:
            return f"You try to use the {c.noun}, but you don't have it."
        return "Use what on what?"

    def _tape_hose(self) -> str:
        if self.room != "generator":
            return "The fuel hose is here, in the generator room. The tape is " \
                   "wherever your pockets are."
        if not self.is_lit():
            return "It's too dark to fiddle with things."
        if self.hose_fixed:
            return "The hose is already taped. It is holding with a confidence " \
                   "that borders on annoying."
        if "ducttape" not in self.inventory:
            return "The hose is cut clean and it wants tape. You don't have " \
                   "tape. Somewhere in this building, tape is waiting."
        self.hose_fixed = True
        self.add_score(10)
        return ("You wrap the cut in three tight spirals of duct tape. It "
                "holds. It holds in a way that suggests the tape is "
                "overqualified. [The fuel hose is repaired.]")

    def _plunger_fusebox(self) -> str:
        if self.room != "generator":
            return "The fuse box is on the generator, in the generator room."
        if not self.is_lit():
            return "It's too dark to fiddle with things."
        if self.fuse_taken:
            return "The fuse box is empty. It has no remaining secrets, or " \
                   "it is being modest."
        if "plunger" not in self.inventory:
            return "The fuse is jammed hard against the back of the box. It " \
                   "will need suction, and a commitment."
        self.fuse_taken = True
        self.inventory.add("fuse")
        del self.item_loc["fuse"]
        self.add_score(10)
        return ("You cup the plunger over the fuse and give one careful, "
                "professional pull. The fuse comes free with a sound like a "
                "tiny victory fanfare. [You now have the fuse. It will want "
                "a home: the main breaker, substation.]")

    def _fuse_breaker(self) -> str:
        if self.room != "substation":
            return "The main breaker is in the substation. The fuse should " \
                   "follow it there."
        if self.fuse_in_breaker:
            return "The fuse is already seated. The socket is not interested " \
                   "in a second one."
        if "fuse" not in self.inventory:
            return "The breaker's socket is empty and personal about it. " \
                   "It wants a fuse."
        self.inventory.discard("fuse")
        self.fuse_in_breaker = True
        return "You seat the fuse into the empty socket. It fits like an " \
               "apology. Now the breaker can mean something."

    # ---------------------------------------------------------------- start
    def _insert_tape(self, tape: str) -> str:
        if self.room != "server":
            return ("The backup drive is in the server room. It has three "
                    "bays and a policy.")
        if not self.breaker_on:
            return ("The backup drive is dead. Three empty bays, no power, "
                    "and the whole apparatus taking this personally. It will "
                    "need building power first.")
        if tape not in self.inventory:
            return f"You don't have the {d.ITEMS[tape].name}."
        if tape in self.backup_tapes:
            return (f"That bay already has the {d.ITEMS[tape].name} in it. "
                    "The drive is not a recycling bin.")
        self.inventory.discard(tape)
        self.backup_tapes.add(tape)
        self.add_score(10)
        if len(self.backup_tapes) == 1:
            return ("The drive takes VOL. 1. The room holds its breath. The "
                    "static resolves, for half a second, into a face. It is "
                    "Bernard. It is not surprised.")
        if len(self.backup_tapes) == 2:
            return ("The drive takes VOL. 2. The temperature drops, then — "
                    "slowly — rises. Bernard is listening. 'That's the one I "
                    "regret,' he says. 'That's the one I'm proudest of. Same "
                    "tape. Don't ask.'")
        # the third tape: completion
        self.backup_done = True
        self.ghost_peaceful = True
        self.add_score(20)
        if not self.keycard_given:
            self.keycard_given = True
            self.inventory.add("keycard")
        return (
            "The drive takes VOL. 3. The three bays hum together, a chord "
            "more than a sound. On the drive's screen, in steady hand-keyed "
            "letters: DONE.\n"
            "Bernard... is... warm. The cold leaves the room the way a debt "
            "leaves a ledger. 'That's it,' he says. 'That's the one. You can "
            "go, kid. The door code is my year.'\n"
            "He reaches into himself and hands you a card: the MASTER "
            "KEYCARD. It is cold in your hand and then, briefly, warm.\n\n"
            "[OBJECTIVE COMPLETE: Complete Bernard's final backup. You now "
            "carry the master keycard.]"
        )

    def _vcr_eject(self) -> str:
        if self.room != "breakroom":
            return ("The VCR is in the break room. It is playing nothing. It "
                    "has always been playing nothing.")
        if not self.is_lit():
            return "It's too dark to fiddle with things."
        if "tape1" not in self.item_loc:
            return "The VCR is empty now. It is playing nothing, at ease."
        if "paperclip" not in self.inventory:
            return ("The tape is wedged past the door, and the eject button "
                    "has been a rumor since 1987. It would need something "
                    "thin, patient, and pointy.")
        self.inventory.add("tape1")
        del self.item_loc["tape1"]
        self.add_score(10)
        return ("You slide the paperclip through the mechanical release. The "
                "door clicks. VOL. 1 comes out, and the VCR exhales like a "
                "small animal that has been held down for forty years.")

    def _vending(self) -> str:
        if not self.breaker_on:
            self.vending_tried = True
            return ("You press the buttons. The vending machine ends in a "
                    "sad sigh.")
        if "coffee" in self.inventory:
            return ("You already have the coffee. The machine is watching "
                    "you with what you hope is pride.")
        if "coin" in self.inventory:
            self.inventory.discard("coin")
            self.inventory.add("coffee")
            self.add_score(5)
            return ("You insert your 1986 coin. The machine accepts it with "
                    "a rattle of old gears and a sound like a small "
                    "resurrection. OUT: one coffee, BERNARD'S RECIPE.")
        if "freecoffee" in self.seen:
            return ("The machine has already given you its free coffee. It "
                    "is now at a loss for miracles.")
        self.seen.add("freecoffee")
        self.inventory.add("coffee")
        self.add_score(5)
        return ("One button glows: FREE. BERNARD'S RECIPE. The machine "
                "dispenses a coffee with the ceremony of a funeral home "
                "pouring the last glass.")

    def _start(self, c) -> str:
        if c.noun and self.resolve(c.noun) == "ghost":
            return ("Starting the ghost is not in the runbook. He is, in "
                    "fact, already up. He is always up. He has been up "
                    "since 1987.")
        if c.noun and self.resolve(c.noun) == "vending":
            return self._vending()
        if c.noun and self.resolve(c.noun) == "generator":
            pass
        if self.room != "generator":
            return "The generator is in the generator room. It is named after " \
                   "itself. It will not be coming to you."
        if not self.is_lit():
            return "It's too dark to pull a cord with conviction."
        if self.generator_running:
            return "It's already humming. You can leave it humming."
        if not self.hose_fixed:
            return ("The pull cord gives way, the engine coughs, sputters, "
                    "and dies. The fuel hose is cut clean — no fuel is "
                    "reaching the engine, and the engine has noticed.")
        self.generator_running = True
        self.add_score(10)
        return ("The pull cord gives way. The engine snarls, settles, and "
                "finds a steady industrial hum. A great victory — except "
                "that nothing in the building comes on. The main breaker is "
                "up in the substation, and it is still dead. [Generator "
                "running. Power still needs a path to the building.]")

    # ----------------------------------------------------------------- pull
    def _pull(self, c) -> str:
        if c.noun and self.resolve(c.noun) == "breaker":
            pass
        if self.room != "substation":
            return "The main breaker is in the substation. It is brooding " \
                   "there."
        if self.breaker_on:
            return "The breaker is already on. The building is lit. You feel " \
                   "oddly promoted."
        if not self.fuse_in_breaker:
            return "The handle throws with alarming freedom. It means " \
                   "nothing — the breaker has no fuse."
        self.breaker_on = True
        self.add_score(20)
        return (
            "You throw the main breaker. The substation inhales. Every light "
            "in the building comes on at once, as if the building has been "
            "holding its breath since 1987 and finally remembers how to be "
            "a building. Somewhere, the vending machine makes a sound like a "
            "cash register in a dream.\n\n"
            "[OBJECTIVE COMPLETE: Restore generator power.]"
        )

    # ----------------------------------------------------------------- read
    def _read(self, c) -> str:
        iid = self.resolve(c.noun)
        if iid == "runbook":
            if self.room != "office":
                return "The laptop is in the office. It is at 3% and will be " \
                       "at 0% whenever."
            if "runbook" in self.seen:
                return "The runbook is still on the page that matters. You " \
                       "have already learned the part that mattered."
            self.seen.add("runbook")
            self.add_score(5)
            return (
                "The emergency runbook, page 1:\n"
                " 1. GENERATOR — fuel line service is in the generator room. "
                "A cut line is held by DUCT TAPE until Thursday.\n"
                " 2. FUSES — the main breaker (substation) takes the fat "
                "fuse. If jammed, a PLUNGER is the approved extraction "
                "tool. Do not use teeth. (This was added in red ink.)\n"
                " 3. BLAST DOOR — keypad code is set to the ORIGINAL "
                "INSTALLATION YEAR, per policy 87-114.\n"
                " 4. PERSONNEL — if you meet Bernard, be polite. He was well "
                "liked. (This line has coffee on it.)\n"
                "The battery dies as you finish. The screen holds, one last "
                "act of loyalty."
            )
        if iid == "mainframe":
            if self.room != "server":
                return "The mainframe is in the server room. It has always " \
                       "been in the server room."
            if not self.breaker_on:
                return "The CRT is dead. Its fan spins down, very slowly, " \
                       "with the patience of the elderly."
            if "mainframe" in self.seen:
                return "The mainframe still shows Bernard's last log. You " \
                       "know it by heart now. That's the part about loss."
            self.seen.add("mainframe")
            self.add_score(10)
            return (
                "The CRT wakes. A cursor blinks, then text, hand-keyed and "
                "perfect:\n"
                " LAST ENTRY — 03:12, 7 NOV 1987\n"
                " OUTAGE IN PROGRESS. I HAVE STARTED THE FINAL BACKUP. "
                "THREE TAPEs. IF I DO NOT RETURN: COMPLETE IT.\n"
                " I LEFT THEM WHERE I LEFT MY LIFE. ONE WHERE I LAUGHED. "
                "ONE WHERE I DID NOT. ONE IN A TROPHY I DID NOT DESERVE.\n"
                " THE DOOR CODE IS MY YEAR. IT HAS ALWAYS BEEN MY YEAR.\n"
                " — B.K.\n"
                "The cursor blinks. You have a job to do."
            )
        if iid is None:
            return f"There is nothing to read on the {c.noun or 'air'}."
        return f"The {d.ITEMS[iid].name} does not have a reading in it."

    # ------------------------------------------------------------- score etc
    def _score(self, c) -> str:
        objs = [
            ("Restore generator power", self.breaker_on),
            ("Complete Bernard's final backup", self.backup_done),
            ("Acquire the master keycard", "keycard" in self.inventory),
            ("Unlock the blast door", self.door_open),
        ]
        lines = ["OBJECTIVES (all four required to escape):"]
        for name, done in objs:
            lines.append(f"[{'x' if done else ' '}] {name}")
        lines.append(f"Score: {self.score}   (turn {self.turn})")
        return "\n".join(lines)

    def _help(self, c) -> str:
        return (
            "COLD STORAGE — a haunted data center adventure.\n"
            "Commands: look (l/x), go/directions (n/s/e/w), inventory (i),\n"
            "take (t), drop (d), use X on Y, read, start, pull, shake,\n"
            "eat, drink, score (objectives), help.\n"
            "Tip: this building respects competence. Show it some."
        )

    def _quit(self, c) -> str:
        if self.escaped:
            self._force_quit = True
            return "THE END"
        return ("The blast door does not open out of spite. This is a "
                "haunted game: there is no leaving until you earn it. "
                "Type 'score' to see what still needs doing.")

    # ------------------------------------------------------------- gags etc
    def _eat(self, c) -> str:
        iid = self.resolve(c.noun)
        if iid == "sandwich" and "sandwich" in self.inventory:
            self.inventory.discard("sandwich")
            self.sandwich_eaten = True
            return ("The sandwich is from 1987. Your stomach files a formal "
                    "complaint, cites the label ('DO NOT FEED THE RATS'), "
                    "and then simply declines to be involved.")
        if iid is None:
            return f"You don't have any {c.noun or 'food'}."
        return f"The {d.ITEMS[iid].name} is not food. It is being very clear about this."

    def _drink(self, c) -> str:
        if self.resolve(c.noun) == "coffee" and "coffee" in self.inventory:
            self.inventory.discard("coffee")
            return ("It is the right temperature. You are not sure this is "
                    "allowed, anywhere, by anyone. You drink it anyway. It "
                    "was worth the forty years of waiting.")
        return "You drink the air. The air is fine, honestly. Room temperature."

    def _heat(self, c) -> str:
        if self.resolve(c.noun) == "sandwich":
            return "The microwave is dead. The sandwich remains ambient. " \
                   "The ghost, from the next room, mutters: 'Finally. " \
                   "Something in this building works correctly.'"
        return f"Heating the {c.noun or 'thing'} is not a service this " \
               f"building offers."

    def _wait(self, c) -> str:
        return "The building does not hurry. It has forty years of practice."

    def _open(self, c) -> str:
        if self.resolve(c.noun) in ("door", "blast door") or (
                self.room == "lobby" and c.noun in (None, "door")):
            return self._blast_door_text()
        return f"Opening the {c.noun or 'thing'} changes nothing. It was " \
               f"always going to change nothing."

    def _close(self, c) -> str:
        return "You close the {x}. It was already closed. It is closed in a way that has become personal.".format(x=c.noun or "thing")

    def _shake(self, c) -> str:
        iid = self.resolve(c.noun)
        if iid == "trophy" and "trophy" in self.inventory:
            self.trophy_shakes += 1
            if not self.tape3_in_trophy:
                return "The trophy is empty now. It is just a trophy. It is " \
                       "doing very well."
            if self.trophy_shakes >= 2:
                self.tape3_in_trophy = False
                return ("You shake again, and a VHS tumbles out: BERNARD'S "
                        "FINAL BACKUP, VOL. 3. He hid his last night shift "
                        "inside a hardware-store trophy. Of course he did.")
            return ("The trophy rattles. Something inside rattles back, "
                    "eagerly, like it has been waiting for this exact "
                    "gesture. (Perhaps it wants to come out.)")
        if iid is None:
            return f"You shake the {c.noun or 'air'}. The air is unmoved."
        return f"The {d.ITEMS[iid].name} does not rattle. It is being calm about this."

    def _ask(self, c) -> str:
        a = self.resolve(c.noun)
        if a == "ghost":
            topic = (c.noun2 or "").lower()
            if any(w in topic for w in ("code", "password", "door", "number")):
                if self.ghost_peaceful:
                    return ("'The code? 1987. My year. You'd think I'd pick "
                            "a password with more flair, but I was "
                            "mid-outage.'")
                return ("'The door? The door is a question with your name on "
                        "it. Answer the rest first, kid.'")
            if any(w in topic for w in ("tape", "backup", "regret", "where")):
                return ("'Three tapes. I left them where I left my life: one "
                        "where I laughed, one where I didn't, one in a "
                        "trophy I didn't deserve.'")
            if "who" in topic or topic == "":
                return ("'Bernard Kowalski. Night shift, 1987 to whenever. I "
                        "am the reason this building still has standards.'")
            return "'Is that a question, or a ticket?'"
        if a is None:
            n = c.noun or "air"
            return f"You ask the {n} a question. The {n} is not qualified to answer."
        return f"The {d.ITEMS[a].name} does not take questions."

    def _ghost_look(self) -> str:
        if self.ghost_peaceful:
            return ("Bernard. No longer translucent — more like... present. "
                    "The cold is gone, and he glows the faint warm gold of a "
                    "successful backup. His posture is the same. His "
                    "posture was always the same.")
        return ("Bernard. Translucent, short-sleeved dress shirt, posture "
                "still corrected by four decades of habit. His left hand "
                "taps the air at the rhythm of a keyboard that no longer "
                "exists.")

    def _feed_gary(self) -> str:
        if self.room != "breakroom":
            return "Gary is in the break room. Gary has always been in the " \
                   "break room. Gary is the break room."
        if "sandwich" not in self.inventory:
            return "You offer Gary a sandwich you do not have. Gary, to his " \
                   "credit, asks for the sandwich to be produced."
        self.inventory.discard("sandwich")
        self.gary_fed = True
        self.add_score(5)
        return ("You break off a piece of 1987 turkey and hold it out. Gary "
                "considers you. Gary accepts. This is the most important "
                "relationship of your career, and you intend to log it.")

    def _gag(self, c) -> str:
        v = c.verb
        if v in ("pray", "pray to"):
            return "You pray. The building, which is not listening, pretends to."
        if v == "exorcise":
            return "You exorcise. The exorcism is exorcised. You both lose."
        if v == "dance":
            return "You do a small, brave dance. The fluorescent light " \
                   "flickers in what you choose to interpret as applause."
        if v == "scare":
            return "You attempt to scare the room. The room has been down " \
                   "since 1987; it has a forty-year head start."
        if v == "apologize":
            return "You apologize to the room. The room, which has never " \
                   "once apologized to you, accepts this."
        if v == "hire":
            return "You cannot hire what is dead. Its union is... complicated."
        if v == "sue":
            return "You consider suing. The building has been in this exact " \
                   "litigation stance since 1987. You are the new party."
        if v == "kill":
            return "You are here to fix things, not to start new things."
        if v == "reboot":
            return "Reboot is a strong word. In 1987 we just walked away " \
                   "and came back. It's called 'night shift.'"
        if v == "sudo":
            return "In 1987, kid. We ran as root and called it a day."
        if v == "git":
            return "git blame: it was Bernard. It's always been Bernard."
        return (f"You {v}. Nothing happens. The building notes this and "
                f"may, later, reference it.")


# convenience for engine/tests
def new_game() -> GameState:
    return GameState()