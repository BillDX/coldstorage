# COLD STORAGE — A Haunted Data Center Adventure

A standalone, Infocom-style text adventure in Python. You are a junior sysadmin
let into an "abandoned" data center to fix its servers. The door seals behind you.
Bernard, a sysadmin who died in the 1987 Great Outage, is still on night shift.

## Goal

Fun first, solvable always, logical gates. Four objectives required to escape:

1. **Restore generator power** (fix cut fuel hose → extract jammed fuse → start
   generator → insert fuse + throw main breaker at substation)
2. **Complete Bernard's final backup** (find 3 tapes, insert into backup drive)
3. **Acquire master keycard** (Bernard hands it over, automatically, once at peace)
4. **Unlock the blast door** (power on + keypad code 1987 + master keycard)

## Map

```
archive -- security -- lobby -- corridor -- breakroom -- substation -- generator
                          |        |         |
                    (blast door)  |      bathroom
                                  +-- office -- server
```

- Dark until power (or flashlight): security, archive, breakroom, bathroom, substation, generator
- Lit-ish always: lobby, corridor (emergency), office (flickering), server (UPS glow)

## Items & sources (single source each)

| item        | source |
|-------------|--------|
| flashlight  | security counter (gropable in the dark) |
| keyring     | office desk; opens corridor locker |
| sandwich    | corridor locker (keyring) |
| ducttape    | breakroom janitor shelf |
| paperclip   | breakroom desk drawer |
| plunger     | bathroom |
| screwdriver | office tool drawer |
| fuse        | generator spare box (jammed → plunger) |
| gascan      | generator (full; flavor + "use gascan on generator" alternative start) |
| coin        | lobby bench |
| trophy      | office shelf; shake → tape3 falls out |
| tape1       | breakroom VCR (wedged → paperclip) |
| tape2       | archive shelf ("BERNARD'S REGRETS, VOL. 2") |
| tape3       | inside trophy |
| runbook     | office laptop (read → hints: code = original install year, hose fix, plunger tip) |
| keycard     | granted by Bernard after backup |
| coffee      | vending machine (works after power; coin or free) |

## Key objects

- `hose` (generator): `use tape on hose`
- `fusebox` (generator): `use plunger on fusebox` → take fuse
- `vcr` (breakroom): `use paperclip on vcr` → tape1
- `mainframe` (server): after power → Bernard's logs + hints
- `breaker` (substation): `use fuse on breaker`, then `throw breaker`
- `backupdrive` (server): insert tape1..3 → backup complete
- `keypad` + `cardreader` (lobby blast door): code 1987 + keycard → open → escape

## Ghost (Bernard)

- Lives in `server`. Agitated until backup complete: blocks the backup drive,
  delivers banter. Peaceful after: grants keycard, hints at code ("my year").
- Non-required gag commands: pray, exorcise, dance, git blame, sudo, reboot ghost,
  hire, sue, scare, apologize.
- Rat "Gary" (breakroom, toaster-sized): feed sandwich → friendship (score).

## Architecture

- `coldstorage/`
  - `game/__init__.py`, `parser.py`, `data.py` (items/rooms defs), `ghost.py`,
    `game.py` (GameState + rules), `engine.py` (loop/UI), `__main__.py`
  - `tests/` — parser, data integrity, power chain, backup/keycard,
    door/ending, full playthrough, no-deadlock sanity
  - stdlib-only runtime; pytest dev dep via uv

## TDD process (strict red/green)

1. scaffold (uv, pytest, git, PLAN/README)
2. parser: red → green
3. data integrity: red → green
4. game core + power chain: red → green
5. ghost/backup/keycard: red → green
6. door + ending + engine + full playthrough: red → green
7. humor polish pass, full suite green, README, done

## Status

- [x] Design locked
- [x] Step 1 scaffold
- [x] Step 2 parser
- [x] Step 3 data integrity
- [x] Step 4 power chain
- [x] Step 5 ghost/backup/keycard
- [x] Step 6 door/ending/engine/playthrough
- [x] Step 7 polish
- [x] Post-polish: giant ASCII title banner; quit always ends the game
      (exit/leave only suggest quit); README rewritten for workshop context
- [ ] Push to GitHub (sandbox cannot authenticate; owner must push)

## Handoff (2026-10-23)

- **Game is complete and shipped-ready.** 68 tests green (`uv run pytest -q`),
  deterministic, full playthrough validated by `tests/test_playthrough.py`.
  Play: `uv run python -m game`.
- **Git:** all game work is pushed to `origin/main`; authors are BillDX +
  GitHub noreply (964503+BillDX@users.noreply.github.com). At handoff, local
  `main` carries one extra commit (this PLAN.md update). Owner: `git push -u
  origin main` from their own terminal — this sandbox cannot read git/gh
  credentials and must not be pointed at them.
- **Ongoing race to be aware of:** README.md is edited in three places
  (this repo, the GitHub web UI, and the agent). After any web-UI edit,
  fetch/merge before pushing, or pushes get rejected (happened twice).
- **Sandbox note:** the agent's shell cannot read `~/.config/gh` or prompt
  for credentials ("operation not permitted" / "Device not configured").
  That is intentional confinement, not a bug to fix.
- **Ideas, not required:** per-room flavor in dark text is done; possible
  future work — extra gags, a `look` that doesn't reprint the whole
  description, or a second playable ending (e.g. let Gary out too).
