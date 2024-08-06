# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Francesco Gazzetta
# Copyright (C) 2023 Samuel Sloniker

"""Bible reader
~~~~~~~~~~~~~~~

This app is a Bible reader for Wasp-os. It relies on a properly coded Bible
file existing at `bible.txt`.

Text display code is based in part on the Morse app by Francesco Gazzetta.


.. figure:: res/screenshots/BibleApp.png
    :width: 179
"""

import os
import io
import wasp
import icons
import fonts
import json
from math import floor
from micropython import const

_ALL_BOOKS = [
    "01_Genesis.txt",
    "02_Exodus.txt",
    "03_Leviticus.txt",
    "04_Numbers.txt",
    "05_Deuteronomy.txt",
    "06_Joshua.txt",
    "07_Judges.txt",
    "08_Ruth.txt",
    "09_1_Samuel.txt",
    "10_2_Samuel.txt",
    "11_1_Kings.txt",
    "12_2_Kings.txt",
    "13_1_Chronicles.txt",
    "14_2_Chronicles.txt",
    "15_Ezra.txt",
    "16_Nehemiah.txt",
    "17_Esther.txt",
    "18_Job.txt",
    "19_Psalms.txt",
    "20_Proverbs.txt",
    "21_Ecclesiastes.txt",
    "22_Song_of_Solomon.txt",
    "23_Isaiah.txt",
    "24_Jeremiah.txt",
    "25_Lamentations.txt",
    "26_Ezekiel.txt",
    "27_Daniel.txt",
    "28_Hosea.txt",
    "29_Joel.txt",
    "30_Amos.txt",
    "31_Obadiah.txt",
    "32_Jonah.txt",
    "33_Micah.txt",
    "34_Nahum.txt",
    "35_Habakkuk.txt",
    "36_Zephaniah.txt",
    "37_Haggai.txt",
    "38_Zechariah.txt",
    "39_Malachi.txt",
    "40_Matthew.txt",
    "41_Mark.txt",
    "42_Luke.txt",
    "43_John.txt",
    "44_Acts.txt",
    "45_Romans.txt",
    "46_1_Corinthians.txt",
    "47_2_Corinthians.txt",
    "48_Galatians.txt",
    "49_Ephesians.txt",
    "50_Philippians.txt",
    "51_Colossians.txt",
    "52_1_Thessalonians.txt",
    "53_2_Thessalonians.txt",
    "54_1_Timothy.txt",
    "55_2_Timothy.txt",
    "56_Titus.txt",
    "57_Philemon.txt",
    "58_Hebrews.txt",
    "59_James.txt",
    "60_1_Peter.txt",
    "61_2_Peter.txt",
    "62_1_John.txt",
    "63_2_John.txt",
    "64_3_John.txt",
    "65_Jude.txt",
    "66_Revelation.txt",
]


def file_to_book_name(file_name):
    return file_name.split("_", 1)[1].replace("_", " ")[:-4]


class FileSegment(io.StringIO):
    def __init__(self, file, offset, length):
        super().__init__()
        self.file = file
        self.offset = offset
        self.length = length
        self.position = 0

    def read(self, size=-1):
        if size == -1:
            remaining_bytes = self.length - self.position
        else:
            remaining_bytes = min(size, self.length - self.position)

        self.file.seek(self.offset + self.position)
        data = self.file.read(max(remaining_bytes, 0))
        self.position += len(data)

        return data

    def seek(self, position):
        if position < 0:
            raise ValueError("negative seek position")

        self.position = position
        return position

    def tell(self):
        return self.position

    def close(self):
        self.file.close()


class BibleApp:
    NAME = "Bible"

    # 2-bit RLE, 96x64, generated from res/icons/bible_icon.png, 245 bytes
    ICON = (
        b"\x02"
        b"`@"
        b"\x15@*A\x80r\xb1B,\xb4A+\xb5A*\xb5"
        b"A*\xb6*\xb6*\xb6*\x99\xc0\xcc\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x8c\xdd\x8d*\x8c\xdd"
        b"\x8d*\x8c\xdd\x8d*\x8c\xdd\x8d*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4"
        b"\x99*\x99\xc4\x99*\x99\xc4\x99*\x99\xc4\x99*\xb6*"
        b"\xb6*\xb6*\xb5A*\xb5A*\xb4A+A\xb1B"
        b"3@\xb4C?\x1eC?\x1eC?\x1eC?\x1eC"
        b"?\x02"
    )

    def __init__(self):
        pass

    def get_books(self):
        for file_name in _ALL_BOOKS:
            try:
                open("/flash/bible/KJV/" + file_name).close()
            except OSError:
                continue

            yield file_name

    def get_text(self, file_name, chapter):
        file = open("/flash/bible/KJV/" + file_name)

        magic = file.readline()
        index_line = file.readline()

        index = []
        position = len(magic + index_line)

        for length_str in index_line.strip().split(","):
            length = int(length_str)
            index.append(
                (
                    position,
                    length,
                )
            )
            position += length

        location, length = index[chapter - 1]
        return FileSegment(file, location, length)

    def get_chapters(self, file_name):
        with open("/flash/bible/KJV/" + file_name) as f:
            f.readline()
            return len(f.readline().split(","))

    def foreground(self):
        draw = wasp.watch.drawable
        draw.fill()

        draw.string("Ready", 0, 108, width=240)

        wasp.system.request_event(
            wasp.EventMask.TOUCH
            | wasp.EventMask.SWIPE_LEFTRIGHT
            | wasp.EventMask.SWIPE_UPDOWN
        )
