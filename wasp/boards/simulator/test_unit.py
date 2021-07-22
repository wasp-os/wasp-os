import draw565
import fonts
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

def test_font_height(draw):
    assert 24 == draw.bounding_box('A')[1]

    draw.set_font(fonts.sans28)
    assert 27 == draw.bounding_box(None)[1]

    draw.set_font(fonts.sans36)
    assert 36 == draw.bounding_box('0')[1]

def test_font_width(draw):
    for f in (fonts.sans24, fonts.sans28, fonts.sans36):
        draw.set_font(f)

        assert 0 == draw.bounding_box('0000')[0] % 4

        if f.max_ch() >= 90:
            assert draw.bounding_box('IIII')[0] < draw.bounding_box('WWWW')[0]

@pytest.mark.parametrize("input,expected", (
    ('abc', [0, 3]),
    ('one.two', [0, 7]),
    ('one two', [0, 7]),
    ('one two three', [0, 13]),
    ('abcdefghijklmnopqrstuvwxyz', [0, 17, 26]),
    ('abcdefghijklm nopqrstuvwxyz', [0, 14, 27]),
    ('abcde fghij klmno pqrst uvwxyz', [0, 18, 30]),

))
def test_wrap(draw, input, expected):
    assert draw.wrap(input, 240) == expected
