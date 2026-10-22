# COLD STORAGE

**A Haunted Data Center Adventure** — a standalone Infocom-style text game in Python entirely by local/sovereign AI on a Macbook M3.

A client bought an abandoned data center off the internet and sent you to
fix its servers. The blast door sealed behind you. The building has been
offline since the Great Outage of 1987. The night shift, apparently, was
never relieved.

Your job: do your job, survive the hauntings, and get out.

## Play

```
cd coldstorage
uv run python -m game
```

## Controls

Some Sample Classic Zork-style verbs:

| Command | Example |
|---|---|
| Go | `go north`, `e`, `s`, `w` (bare directions are always fine) |
| Look | `look`, `l` |
| Take / drop | `take tape 1`, `drop trophy` |
| Use | `use plunger on fuse box` |
| Read / examine | `read runbook`, `read mainframe`, `examine trophy` |
| Start / pull / shake / open | `start generator`, `pull breaker`, `shake trophy` |
| Ask / feed / give | `ask ghost about the door code`, `feed gary` |
| Status | `score`, `inventory`, `i`, `help`, `quit` |
(This is by no means complete.  Experiment and enjoy.)

## The four game objectives

To escape the haunted data center you'll need to . `score` shows your progress.

1. **Restore generator power** — the building is dark. Follow the runbook.
2. **Complete Bernard's final backup** — for a ghost
   who has been holding his breath since 1987.
3. **Acquire the master keycard** — Bernard has opinions about it.
4. **Unlock the blast door** — Freedom and sunlight beyond.

You do not have to be a clever sysadmin. You have to be a *persistence*
sysadmin.

## Design notes

- **This was written for a workshop of local/sovereign AI.** This adventure was entirely written by a Qwen3.8 LLM that fit into 16GB of ram on a Macbook M3 and its human prompter, Bill.  Bill used a Pi coding harness, with some sandbox safety add-ons, and minimal agents.md skills.md to maximize available context and token throughput.   
- **Red/green TDD throughout.** Every system was written as a failing test
  first, then made to pass. The crown jewel is
  `tests/test_playthrough.py`, which replays a full canonical solution
  (`tests/solution.py`) through the game engine and asserts that all four
  objectives complete, the player escapes, the score is earned, and every
  non-latent item is in exactly one place at the end.
- **The world is a state machine.** Rooms, items, flags, and flags-in-waiting
  (the *latent* set) live in `game/data.py`. Rules live in
  `game/game.py`. Parsing lives in `game/parser.py`. The loop lives in
  `game/engine.py`.
- **Humor is a core feature, not a garnish.** The fluorescent light flickers
  "like it is buffering." Gary the rat has union rights. Ghost-Bernard will not
  give up the keycard until the backup is done, because it is *his* final
  shift, and the dead are very bad at letting go of the punch card.
- **The darkness is fair.** Part of the LLM's test harness was making sure full-playthroughs were always achievable.  Dark rooms hide their items and block
  interactions, but they tell you they are dark, and light is always
  reachable. No item is unreachable without a puzzle, state, or tool, and every tool is
  findable in a lit room.
- **No random number generator.** The game is fully deterministic. Same
  input, same haunting.

## Test

```
uv run pytest -q
```

54 tests, all green. Includes the full playthrough.

## A note on the score

Infocom awarded 0–350 points and ranked you. We award up to about 210
points and rank you as "a person who got out," which, in this economy, is
the only ranking that matters.

---

*Written by Bill McIntyre — GitHub: [BillDX](https://github.com/BillDX)*

*© 2026, Atomocom LLC. All rights reserved, released, and haunted.*
