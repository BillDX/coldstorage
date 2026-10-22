"""The giant ASCII intro banner."""
from game.engine import run, title_banner


def test_banner_is_five_lines():
    lines = title_banner("COLD STORAGE").split("\n")
    assert len(lines) == 5


def test_banner_has_uniform_line_width():
    lines = title_banner("COLD STORAGE").split("\n")
    widths = {len(line) for line in lines}
    assert len(widths) == 1, widths


def test_banner_is_giant():
    lines = title_banner("COLD STORAGE").split("\n")
    assert len(lines[0]) >= 60


def test_banner_is_pure_ascii():
    for ch in title_banner("COLD STORAGE"):
        assert ord(ch) < 128, repr(ch)


def test_banner_uses_block_glyphs():
    # chunky enough to be seen from across the room
    assert "#" in title_banner("COLD STORAGE")


def test_banner_appears_at_game_start():
    out = run(["quit"])
    assert title_banner("COLD STORAGE") in out


def test_subtitle_and_copyright_still_present():
    out = run(["quit"])
    assert "A HAUNTED DATA CENTER ADVENTURE" in out
    assert "1987" in out