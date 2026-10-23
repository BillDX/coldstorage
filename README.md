# COLD STORAGE

**A Haunted Data Center Adventure** — a standalone Infocom-style text game in Python, written entirely by a local/sovereign AI on a MacBook Pro (M3).

A client bought an abandoned data center off the internet and sent you to
fix its servers. The blast door sealed behind you. The building has been
offline since the Great Outage of 1987. The night shift, apparently, was
never relieved.

Your job: do your job, survive the hauntings, and get out.

## Where this came from

COLD STORAGE was built for a workshop on **Local / Sovereign AI
development and agentic coding**.

It was created **entirely on-device**: a MacBook Pro (M3) — 16GB of RAM —
running a local **Qwen3.8** model that fits inside it, steered by its
human prompter, Bill. Bill used the **pi** coding harness with a few
sandbox safety add-ons and a minimal AGENTS.md / skills setup, to
maximize available context and token throughput. No cloud APIs in the
loop — the workshop point was that the whole thing (design, code, tests,
debugging, even the jokes) was produced by a model running on the
laptop, and the human's job was direction and taste.

The process was strict **red/green TDD**: every system landed as a
failing test first, then got made to pass — and the full game is
validated by an automated playthrough that plays the entire adventure to
its ending and checks the world state at the end. The game was designed
up front to be a **fun, classic Infocom-style adventure** (inventory,
puzzles, darkness, a ghost, a rat with union rights) with multiple
objectives that must *all* be completed to escape.

## Play

```
cd coldstorage
uv run python -m game
```

## Controls

Some sample classic Zork-style verbs:

| Command | Example |
|---|---|
| Go | `go north`, `e`, `s`, `w` (bare directions are always fine) |
| Look | `look`, `l` |
| Take / drop | `take tape 1`, `drop trophy` |
| Use | `use plunger on fuse box` |
| Read / examine | `read runbook`, `read mainframe`, `examine trophy` |
| Start / pull / shake / open | `start generator`, `pull breaker`, `shake trophy` |
| Ask / feed / give | `ask ghost about the door code`, `feed gary` |
| Status | `score`, `inventory`, `i`, `help` |
| Quit | `quit` — always ends the game. (`exit`/`leave` only suggest it.) |

(This is by no means complete. Experiment and enjoy.)

## The four game objectives

To escape the haunted data center you'll need to complete all four.
`score` shows your progress.

1. **Restore generator power** — the building is dark. Follow the runbook.
2. **Complete Bernard's final backup** — three tapes, three rooms, one
   ghost who has been holding his breath since 1987.
3. **Acquire the master keycard** — Bernard has opinions about it.
4. **Unlock the blast door** — freedom and sunlight beyond.

You do not have to be a clever sysadmin. You have to be a *persistence*
sysadmin.

## How it's built

- **The world is a deterministic state machine.** Rooms, items, and flags
  (including a *latent* set of things that come into existence as the
  story progresses) live in `game/data.py`. Rules live in `game/game.py`.
  Parsing lives in `game/parser.py`. The interactive loop lives in
  `game/engine.py`. Same input, same haunting — there is no random number
  generator anywhere.
- **Red/green TDD throughout.** Every system was a failing test first.
  The crown jewel is `tests/test_playthrough.py`, which replays a full
  canonical solution (`tests/solution.py`) through the engine and asserts
  that all four objectives complete, the player escapes, the score is
  earned, and every item is in exactly one place at the end. That
  invariant caught real bugs the unit tests missed (items duplicated
  between room and inventory, consumed items vanishing from the world).
- **The darkness is fair.** Part of the test harness's job was making
  sure full playthroughs were always achievable. Dark rooms hide their
  items and block interactions, but they tell you they're dark, and light
  is always reachable. No item is unreachable without a tool, and every
  tool is findable in a lit room.
- **Humor is a feature, not a garnish.** The fluorescent light flickers
  "like it is buffering." Gary the rat has union rights. Bernard will not
  give up the keycard until the backup is done, because it is *his* final
  shift, and the dead are very bad at letting go of the punch card.

## Run the tests

```
uv run pytest -q
```

68 tests, all green — including the full automated playthrough.

## A note on the score

Infocom awarded 0–350 points and ranked you. We award up to about 210
points and rank you as "a person who got out," which, in this economy, is
the only ranking that matters.

---

*Written by Bill McIntyre — GitHub: [BillDX](https://github.com/BillDX)*
*Built locally on an M3 with Qwen3.8 + pi. No clouds were used in the making of this haunting.*

*© 2026, Atomocom LLC. All rights reserved, released, and haunted.*