import draw565
import pytest

@pytest.fixture
def draw():
    """Provide a RGB565 drawing surface.

    Currently most of the draw565 functions will not work since we haven't
    mocked up the display. This limits the testing that we can perform.
    """
    d = draw565.Draw565(None)

    return d

def test_lighten(draw):
    assert draw.lighten(0b00000_000000_00000         ) == 0b00001_000010_00001
    assert draw.lighten(0b00000_000000_00000, 0b00001) == 0b00001_000010_00001
    assert draw.lighten(0b00000_000000_00000, 0b00100) == 0b00100_001000_00100

    assert draw.lighten(0b10000_100000_10000, 0b10000) == 0b11111_111111_11111
    assert draw.lighten(0b11110_111100_11110, 0b00001) == 0b11111_111110_11111
    assert draw.lighten(0b11110_111101_11110, 0b00001) == 0b11111_111111_11111

    assert draw.lighten(0b11111_111111_11111, 0b00001) == 0b11111_111111_11111

    assert draw.lighten(0b10000_010000_01000, 0b10000) == 0b11111_110000_11000
    assert draw.lighten(0b01000_100000_01000, 0b10000) == 0b11000_111111_11000
    assert draw.lighten(0b01000_010000_10000, 0b10000) == 0b11000_110000_11111

def test_darken(draw):
    assert draw.darken(0b00001_000010_00001, 0b00001) == 0b00000_000000_00000
    assert draw.darken(0b00010_000100_00010         ) == 0b00001_000010_00001
    assert draw.darken(0b00010_000100_00010, 0b00001) == 0b00001_000010_00001
    assert draw.darken(0b10000_010000_00100, 0b00001) == 0b01111_001110_00011

    assert draw.darken(0b00000_000000_00000, 0b00001) == 0b00000_000000_00000
    assert draw.darken(0b00001_000001_00001, 0b00001) == 0b00000_000000_00000
    assert draw.darken(0b10000_100000_10000, 0b10001) == 0b00000_000000_00000
    assert draw.darken(0b10000_100010_10010, 0b10001) == 0b00000_000000_00001
    assert draw.darken(0b10000_100100_10010, 0b10001) == 0b00000_000010_00001

