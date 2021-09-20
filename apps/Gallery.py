# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Francesco Gazzetta

"""Image gallery
~~~~~~~~~~~~~~~~~~~~~~~~~

An application that shows images stored in the filesystem.

.. figure:: res/GalleryApp.png
    :width: 179

Only 240x240 images are supported for now.
The images have to be uploaded in the gallery directory.
The images have to be encoded as raw RGB565 data in big endian byte order.
To encode them, you can use ffmpeg:

.. code-block:: sh

    ffmpeg -vcodec png -i my_image.png -vcodec rawvideo -f rawvideo -pix_fmt rgb565be my_image.rgb565

And to upload:

.. code-block:: sh

    ./tools/wasptool --binary --upload my_image.rgb565 --as gallery/my_image
"""

import wasp
import icons

class GalleryApp():
    NAME = 'Gallery'
    # 2-bit RLE, 96x64, generated from res/gallery_icon.png, 370 bytes
    ICON = (
        b'\x02'
        b'`@'
        b'\x1e@\x81d<d<d;f?X\xec2\xf0/'
        b'\xf2-\xf4,\xc3.\xc3,\xc3.\xc3,\xc3.\xc3,'
        b'\xc3.\xc3,\xc3\x04\x80\x1d\xa6\x04\xc3,\xc3\x04\xa6\x04'
        b'\xc3,\xc3\x04\x83\xc0\xd2\xc2\xa1\x04@\xd7C,C\x04'
        b'\x82\xc4\xa0\x04C,C\x04\x81\xc6\x9f\x04C,C\x04'
        b'\x82\xc4\xa0\x04C,C\x04\x83\xc2\x9c\x80\xc1\x81\xc0\x1d'
        b'\xc4\x04C,C\x04\xe0\x83\xc3\x04C,C\x04\xdf\x85'
        b'\xc2\x04C,C\x04\xde\x87\xc1\x04C,C\x04\xdd\x89'
        b'\x04C,C\x04\xdc\x8a\x04C,C\x04\xce\x82\xcb\x8b'
        b'\x04C,C\x04\xcc\x85\xc9\x8c\x04C+D\x04\xca\x89'
        b'\xc6\x8d\x04C*E\x04\xc8\x8d\xc3\x8e\x04C*E\x04'
        b'\xc6\x91\xc2\x8d\x04C*E\x04\xc4\x95\xc2\x8b\x04C*'
        b'E\x04\xc2\x99\xc2\x89\x04C*E\x04\xa6\x04C*E'
        b'\x04\xa6\x04C*E\x04\xa6\x04C+D\x04\xa6\x04C'
        b',C\x04\xa6\x04C,C\x04\x86@CB\x9bC\x04'
        b'\x80\xd7\x83,\x83\x04\xc0\xc1\xc2I\xd5F\x04\x83,\x83'
        b'\x04\xc1L\xcfJ\x04\x83,\x83\x04P\xc7O\x04\x83,'
        b'\x83\x04f\x04\x83,\x83\x04f\x04\x83,\x83\x04f\x04'
        b'\x83,\x83\x04f\x04\x83,\x83\x04f\x04\x83,\x83\x04'
        b'f\x04\x83,\x83\x04f\x04\x83,\x83\x04f\x04\x83,'
        b'\x83\x04f\x04\x83,\x83\x04f\x04\x83,\x83.\x83,'
        b'\x83.\x83,\x83.\x83,\x83.\x83,\xb4-\xb2/'
        b'\xb02\xac?X@\x81f;d<d<d\x1e'
    )

    def foreground(self):
        try:
            self.files = wasp.watch.os.listdir("gallery")
        except FileNotFoundError:
            self.files = []
        # In case some images were deleted, we reset the index every time
        self.index = 0
        self._draw()
        wasp.system.request_event(wasp.EventMask.SWIPE_LEFTRIGHT)

    def background(self):
        # We will read the contents of gallery again on foreground(),
        # so let's free some memory
        self.files = []

    def swipe(self, event):
        if event[0] == wasp.EventType.LEFT:
            increment = 1
        elif event[0] == wasp.EventType.RIGHT:
            increment = -1
        else:
            increment = 0
        self.index = (self.index + increment) % len(self.files)
        self._draw()

    def _draw(self):
        draw = wasp.watch.drawable
        draw.fill()
        if not self.files:
            draw.string('No files', 0, 60, width=240)
            draw.string('in gallery/', 0, 98, width=240)
        else:
            filename = self.files[self.index]
            # The file name will only show until the image overwrites it,
            # so let's put it at the bottom so the user has a chance to see it
            draw.string(filename[:(draw.wrap(filename, 240)[1])], 0, 200)
            file = open("gallery/{}".format(filename), "rb")
            display = wasp.watch.display
            display.set_window(0, 0, 240, 240)

            # We don't have enough memory to load the entire image at once, so
            # we stream it from flash memory to the display
            #TODO: why can't we do it in a single quick write session?
            #display.quick_start()
            buf = display.linebuffer[:2*240]
            read = 1
            while read > 0:
                read = file.readinto(buf)
                #display.quick_write(buf)
                display.write_data(buf)
            #display.quick_end()
            file.close()
