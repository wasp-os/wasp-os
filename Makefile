export PYTHONPATH := $(PWD)/tools/nrfutil:$(PWD)/tools/intelhex:$(PYTHONPATH)

all : bootloader micropython

BOARD=$(error Please set BOARD=)

clean :
	rm -rf \
		bootloader/_build-$(BOARD)_nrf52832 \
		micropython/mpy-cross/build \
		micropython/ports/nrf/build-$(BOARD)-s132

submodules :
	git submodule update --init --recursive

bootloader:
	$(MAKE) -C bootloader/ BOARD=$(BOARD)_nrf52832 all genhex
	python3 -m nordicsemi dfu genpkg \
		--bootloader bootloader/_build-$(BOARD)_nrf52832/$(BOARD)_nrf52832_bootloader-*-nosd.hex \
		--softdevice bootloader/lib/softdevice/s132_nrf52_6.1.1/s132_nrf52_6.1.1_softdevice.hex \
		bootloader.zip
	python3 tools/hexmerge.py \
		bootloader/_build-$(BOARD)_nrf52832/$(BOARD)_nrf52832_bootloader-*-nosd.hex \
		bootloader/lib/softdevice/s132_nrf52_6.1.1/s132_nrf52_6.1.1_softdevice.hex \
		-o bootloader.hex

softdevice:
	micropython/ports/nrf/drivers/bluetooth/download_ble_stack.sh

micropython:
	$(MAKE) -C micropython/mpy-cross
	$(MAKE) -C micropython/ports/nrf \
		BOARD=$(BOARD) SD=s132 \
		FROZEN_MPY_DIR=$(PWD)/wasp
	python3 -m nordicsemi dfu genpkg \
		--dev-type 0x0052 \
		--application micropython/ports/nrf/build-$(BOARD)-s132/firmware.hex \
		micropython.zip

dfu:
	python3 -m nordicsemi dfu serial --package micropython.zip --port /dev/ttyACM0

flash:
	pyocd erase -t nrf52 --mass-erase
	pyocd flash -t nrf52 bootloader.hex

.PHONY: bootloader micropython

