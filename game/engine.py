"""The interactive loop for COLD STORAGE.

run() accepts an optional list of commands (for tests / script playback);
without one it plays on stdin until the ending. In interactive mode every
line is mirrored to the real stdout as it happens, so the player always
sees the room, the prompt, and the game's answers immediately.
"""
from __future__ import annotations

import contextlib
import io
import sys

from .game import GameState

PROMPT = "what now> "

# Chunky 5-row glyphs for the title banner. Pure ASCII, five wide, one
# column of air between letters. Deterministic, of course: same title,
# same scar.
_GLYPHS = {
    "A": [".###.", "#...#", "#####", "#...#", "#...#"],
    "C": [".####", "#....", "#....", "#....", ".####"],
    "D": ["###..", "#..#.", "#..#.", "#..#.", "###.."],
    "E": ["#####", "#....", "####.", "#....", "#####"],
    "G": [".####", "#....", "#.###", "#..#.", ".####"],
    "L": ["#....", "#....", "#....", "#....", "#####"],
    "O": [".####", "#..#.", "#..#.", "#..#.", ".####"],
    "R": ["###..", "#..#.", "###..", "#.#..", "#..#."],
    "S": [".####", "#....", ".###.", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
    " ": ["     "],
}


def title_banner(text: str) -> str:
    """Render a title in giant ASCII block letters (five rows tall)."""
    cells = [_GLYPHS.get(ch.upper(), _GLYPHS[" "]) for ch in text]
    rows = zip(*(c + ["     "] * (5 - len(c)) for c in cells))
    return "\n".join(" ".join(row) for row in rows)


INTRO = (
    title_banner("COLD STORAGE") + "\n\n"
    "A HAUNTED DATA CENTER ADVENTURE\n"
    "© 1987, ∞ Spectral Software\n\n"
    "You are a junior sysadmin. A client bought an 'abandoned' data center\n"
    "off the internet and sent you to fix its servers. The guard let you in\n"
    "and then, with what you can only describe as relief, the blast door\n"
    "sealed behind you. The building has been offline since the Great\n"
    "Outage of 1987. The night shift, apparently, was never relieved.\n\n"
    "Four things stand between you and the daylight. Type 'score' to see\n"
    "them, 'help' to see what your hands can do.\n"
)


class _LiveBuffer(io.StringIO):
    """A StringIO that also mirrors every write to the real stdout."""

    def __init__(self, real) -> None:
        super().__init__()
        self._real = real

    def write(self, s: str) -> int:
        n = super().write(s)
        if s:
            self._real.write(s)
            self._real.flush()
        return n


def run(inputs: list[str] | None = None) -> str:
    """Play the game. Returns the full transcript as a string."""
    interactive = inputs is None
    buf = _LiveBuffer(sys.__stdout__) if interactive else io.StringIO()
    with contextlib.redirect_stdout(buf):
        s = GameState()
        print(INTRO)
        print(s.room_text())
        print()
        lines = None if interactive else [x.strip().lower() for x in inputs]
        i = 0
        while True:
            if interactive:
                try:
                    line = input(PROMPT)
                except EOFError:      # stdin closed: end the session
                    break
                except KeyboardInterrupt:
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
        if not s.escaped and not s._force_quit:
            print("\n(You remain, competently, in the building.)")
    return buf.getvalue()


def main() -> None:
    run()


if __name__ == "__main__":
    main()