#!/usr/bin/env python3
"""Compiles themes for wasp-os"""

from argparse import ArgumentParser, RawTextHelpFormatter
from importlib import import_module
from typing import Tuple

class DefaultTheme():
    """This represents the default theme.

    Import this file and extend the Theme class, only changing the variables.
    Export the resulting class as 'Theme'.
    serialize() should NEVER be overriden!
    """
    BLE_COLOR = 0x7bef
    SCROLL_INDICATOR_COLOR = 0x7bef
    BATTERY_COLOR = 0x7bef
    SMALL_CLOCK_COLOR = 0xe73c
    NOTIFICATION_COLOR = 0x7bef
    ACCENT_MID = 0xb5b6
    ACCENT_LO = 0xbdb6
    ACCENT_HI = 0xffff
    SLIDER_DEFAULT_COLOR = 0x39ff

    def serialize(self) -> bytes:
        """Serializes the theme for use in wasp-os"""
        def split_bytes(x: int) -> Tuple[int, int]:
            return (x & 0xFF, (x >> 8) & 0xFF)
        theme_bytes = bytes([
            *split_bytes(self.BLE_COLOR),
            *split_bytes(self.SCROLL_INDICATOR_COLOR),
            *split_bytes(self.BATTERY_COLOR),
            *split_bytes(self.SMALL_CLOCK_COLOR),
            *split_bytes(self.NOTIFICATION_COLOR),
            *split_bytes(self.ACCENT_MID),
            *split_bytes(self.ACCENT_LO),
            *split_bytes(self.ACCENT_HI),
            *split_bytes(self.SLIDER_DEFAULT_COLOR),
        ])
        return theme_bytes


if __name__ == '__main__':
    parser = ArgumentParser(
        description='''Compiles themes into a format understood by wasp-os.

For the theme to take effect, the resulting string should be put in main.py
like this:

   theme_string = THEME_STRING_GOES_HERE
''',
        epilog=''' To create a theme, import this file and extend the
DefaultTheme class, only changing the variables.

Export the resulting class as 'Theme'.

Example:
--------

theme.py:

    from themer import DefaultTheme

    class Theme(DefaultTheme):
        BLE_ICON_COLOR = 0x041F

shell:

    # NOTE: do not include .py at end of file!
    $ ./themer.py theme
    > b'\\xef{\\xef{\\xef{<\\xe7\\xef{\\xb6\\xb5\\xb6\\xbd\\xff\\xff\\xff9'

main.py:

    ...
    wasp.system.set_theme(
        b'\\xef{\\xef{\\xef{<\\xe7\\xef{\\xb6\\xb5\\xb6\\xbd\\xff\\xff\\xff9')
    ...
''',
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument('input_file', type=str, nargs=1)
    args = parser.parse_args()

    theme = DefaultTheme()
    theme = import_module(args.input_file[0]).Theme()
    print(theme.serialize())

