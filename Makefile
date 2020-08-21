export PYTHONPATH := $(PWD)/tools/nrfutil:$(PWD)/tools/intelhex:$(PYTHONPATH)

all : bootloader reloader micropython

# If BOARD is undefined then set it up so that expanding it issues an
# error. That ensures that rules that expand BOARD will be automatically
# disabled (and give a useful error message) but it creates an additional
# problem which is that we must never unconditionally expand BOARD.
# We workaround this by using BOARD_SAFE for every unconditional
# expansion.
ifdef BOARD
BOARD_SAFE = $(BOARD)
endif
BOARD ?= $(error Please set BOARD=)
VERSION ?= $(patsubst v%,%,$(shell git describe --tags))

clean :
	$(RM) -r \
		bootloader/_build-$(BOARD)_nrf52832 \
		reloader/build-$(BOARD) reloader/src/boards/$(BOARD)/bootloader.h \
		micropython/mpy-cross/build \
		micropython/ports/nrf/build-$(BOARD)-s132 \
		wasp/boards/$(BOARD)/watch.py

submodules :
	git submodule update --init --recursive

bootloader: build-$(BOARD_SAFE)
	$(RM) bootloader/_build-$(BOARD)_nrf52832//$(BOARD)_nrf52832_bootloader-*-nosd.hex
	$(MAKE) -C bootloader/ BOARD=$(BOARD)_nrf52832 all genhex
	python3 tools/hexmerge.py \
		bootloader/_build-$(BOARD)_nrf52832/$(BOARD)_nrf52832_bootloader-*-nosd.hex \
		bootloader/lib/softdevice/s132_nrf52_6.1.1/s132_nrf52_6.1.1_softdevice.hex \
		-o build-$(BOARD)/bootloader.hex
	python3 tools/hex2c.py build-$(BOARD)/bootloader.hex > \
		reloader/src/boards/$(BOARD)/bootloader.h
	python3 -m nordicsemi dfu genpkg \
		--bootloader bootloader/_build-$(BOARD)_nrf52832//$(BOARD)_nrf52832_bootloader-*-nosd.hex \
		--softdevice bootloader/lib/softdevice/s132_nrf52_6.1.1/s132_nrf52_6.1.1_softdevice.hex \
		build-$(BOARD)/bootloader-daflasher.zip

reloader: bootloader build-$(BOARD_SAFE)
	$(MAKE) -C reloader/ BOARD=$(BOARD)
	mv reloader/build-$(BOARD)/reloader.zip build-$(BOARD)/

softdevice:
	micropython/ports/nrf/drivers/bluetooth/download_ble_stack.sh

wasp/boards/$(BOARD_SAFE)/watch.py : wasp/boards/$(BOARD_SAFE)/watch.py.in
	(cd wasp; ../tools/preprocess.py boards/$(BOARD)/watch.py.in > boards/$(BOARD)/watch.py) \
		|| ($(RM) wasp/boards/$(BOARD)/watch.py; false)

micropython: build-$(BOARD_SAFE) wasp/boards/$(BOARD_SAFE)/watch.py
	$(MAKE) -C micropython/mpy-cross
	$(RM) micropython/ports/nrf/build-$(BOARD)-s132/frozen_content.c
	$(MAKE) -C micropython/ports/nrf \
		BOARD=$(BOARD) SD=s132 \
		MICROPY_VFS_LFS2=1 \
		FROZEN_MANIFEST=$(PWD)/wasp/boards/$(BOARD)/manifest.py \
		USER_C_MODULES=$(PWD)/wasp/modules
	python3 -m nordicsemi dfu genpkg \
		--dev-type 0x0052 \
		--application micropython/ports/nrf/build-$(BOARD)-s132/firmware.hex \
		build-$(BOARD)/micropython.zip

build-$(BOARD_SAFE):
	mkdir -p build-$(BOARD)

dfu:
	python3 -m nordicsemi dfu serial --package micropython.zip --port /dev/ttyACM0

flash:
	pyocd erase -t nrf52 --mass
	pyocd flash -t nrf52 bootloader.hex

debug:
	arm-none-eabi-gdb \
		bootloader/_build-$(BOARD)_nrf52832/$(BOARD)_nrf52832_bootloader-*-nosd.out \
		-ex "target extended-remote /dev/ttyACM0" \
		-ex "monitor swdp_scan" \
		-ex "attach 1" \
		-ex "load"

docs:
	$(RM) -rf docs/build/html/*
	$(MAKE) -C docs html
	touch docs/build/html/.nojekyll

sim:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:wasp/boards/simulator:wasp \
	python3 -i wasp/boards/simulator/main.py

.PHONY: bootloader reloader docs micropython

dist: DIST=../wasp-os-$(VERSION)
dist: k9
k9: p8
p8: pinetime
pinetime : mrproper
mrproper :
	$(RM) -r \
		$(DIST) build-* \
		bootloader/_build-* \
		reloader/build-* \
		reloader/src/boards/*/bootloader.h \
		micropython/mpy-cross/build \
		micropython/ports/nrf/build-*
k9 p8 pinetime:
	$(RM) wasp/boards/$@/watch.py
	$(MAKE) BOARD=$@ all
dist: docs
	mkdir -p $(DIST)/docs
	cp COPYING COPYING.LGPL README.rst $(DIST)
	cp -r docs/build/html/* $(DIST)/docs
	cp -r build-*/ $(DIST)
	cp -r tools/ $(DIST)
	(cd $(DIST); ln -s docs/_images/ res)
	find $(DIST) -name __pycache__ | xargs $(RM) -r
	tar -C .. -zcf $(DIST).tar.gz $(notdir $(DIST))

