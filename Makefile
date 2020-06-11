export PYTHONPATH := $(PWD)/tools/nrfutil:$(PWD)/tools/intelhex:$(PYTHONPATH)

all : bootloader reloader micropython

BOARD ?= $(error Please set BOARD=)

clean :
	$(RM) -r \
		bootloader/_build-$(BOARD)_nrf52832 \
		reloader/build-$(BOARD) reloader/src/boards/$(BOARD)/bootloader.h \
		micropython/mpy-cross/build \
		micropython/ports/nrf/build-$(BOARD)-s132

submodules :
	git submodule update --init --recursive

bootloader:
	$(RM) bootloader/_build-$(BOARD)_nrf52832//$(BOARD)_nrf52832_bootloader-*-nosd.hex
	$(MAKE) -C bootloader/ BOARD=$(BOARD)_nrf52832 all genhex
	python3 tools/hexmerge.py \
		bootloader/_build-$(BOARD)_nrf52832/$(BOARD)_nrf52832_bootloader-*-nosd.hex \
		bootloader/lib/softdevice/s132_nrf52_6.1.1/s132_nrf52_6.1.1_softdevice.hex \
		-o bootloader.hex
	python3 tools/hex2c.py bootloader.hex > \
		reloader/src/boards/$(BOARD)/bootloader.h

reloader: bootloader
	$(MAKE) -C reloader/ BOARD=$(BOARD)
	mv reloader/build-$(BOARD)/reloader.zip .

softdevice:
	micropython/ports/nrf/drivers/bluetooth/download_ble_stack.sh

micropython: wasp/boards/pinetime/watch.py
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
		micropython.zip

wasp/boards/pinetime/watch.py : wasp/boards/pinetime/watch.py.in
	(cd wasp; ../tools/preprocess.py boards/pinetime/watch.py.in > \
		                         boards/pinetime/watch.py)

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
	python3 -i wasp/main.py

.PHONY: bootloader reloader docs micropython

