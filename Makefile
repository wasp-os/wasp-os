export PYTHONPATH := $(PWD)/tools/nrfutil:$(PWD)/tools/intelhex:$(PYTHONPATH)

JOBS = -j $(shell nproc)

all : bootloader micropython

clean :
	rm -rf \
		bootloader/_build-nitrogen_nrf52832 \
		micropython/mpy-cross/build \
		micropython/ports/nrf/build-dsd6-s132

submodules :
	git submodule update --init --recursive

bootloader:
	make -C bootloader/ BOARD=nitrogen_nrf52832 $(JOBS) all genhex
	python3 tools/hexmerge.py \
		bootloader/lib/softdevice/s132_nrf52_6.1.1/s132_nrf52_6.1.1_softdevice.hex \
		bootloader/_build-nitrogen_nrf52832/nitrogen_nrf52832_bootloader-*-nosd.hex \
		-o bootloader.hex

micropython:
	make -C micropython/mpy-cross $(JOBS)
	make -C micropython/ports/nrf BOARD=dsd6 SD=s132 $(JOBS)
	python3 -m nordicsemi dfu genpkg \
		--dev-type 0x0052 \
		--application micropython/ports/nrf/build-dsd6-s132/firmware.hex \
		micropython.zip
	
dfu:
	python3 -m nordicsemi dfu serial --package micropython.zip --port /dev/ttyACM0

flash:
	cp bootloader.hex /run/media/$(USER)/MBED

.PHONY: bootloader micropython

