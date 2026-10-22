"""The interactive loop for COLD STORAGE.

run() accepts an optional list of commands (for tests / script playback);
without one it plays on stdin until the ending.
"""
from __future__ import annotations

import contextlib
import io

from .game import GameState

INTRO = (
    "COLD STORAGE\n"
    "A Haunted Data Center Adventure\n"
    "© 1987, ∞ Spectral Software\n\n"
    "You are a junior sysadmin. A client bought an 'abandoned' data center\n"
    "off the internet and sent you to fix its servers. The guard let you in\n"
    "and then, with what you can only describe as relief, the blast door\n"
    "sealed behind you. The building has been offline since the Great\n"
    "Outage of 1987. The night shift, apparently, was never relieved.\n\n"
    "Four things stand between you and the daylight. Type 'score' to see\n"
    "them, 'help' to see what your hands can do.\n"
)

PROMPT = "what now> "


def run(inputs: list[str] | None = None) -> str:
    """Play the game. Returns the full transcript as a string."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        s = GameState()
        print(INTRO)
        print(s.room_text())
        print()
        lines = None if inputs is None else [x.strip().lower() for x in inputs]
        i = 0
        while True:
            if lines is None:
                try:
                    line = input(PROMPT)
                except (EOFError, KeyboardInterrupt):
                    line = "quit"
                line = line.strip().lower()
            else:
                if i >= len(lines):
                    break
                line = lines[i]
                i += 1
            out = s.apply(line)
            print()
            print(out)
            if s._force_quit:
                break
        if not s.escaped:
            print("\n(You remain, competently, in the building.)")
    return buf.getvalue()


def main() -> None:
    run()


if __name__ == "__main__":
    main()