export PYTHONPATH := $(CURDIR)/tools/nrfutil:$(CURDIR)/tools/intelhex:$(PYTHONPATH)

PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest

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
		apps/*.mpy \
		build-$(BOARD) \
		wasp/boards/$(BOARD)/watch.py \
		wasp/apps/user \
		wasp/boards/manifest_user_apps.py \
		wasp/appregistry.py
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

# Avoid a recursive update... it grabs far too much
submodules :
	git submodule update --init
	(cd bootloader; git submodule update --init)
	(cd micropython/ports/nrf; $(MAKE) submodules)
	(cd reloader; git submodule update --init)
	(cd wasp/modules/bma42x-upy; git submodule update --init)

bootloader: build-$(BOARD_SAFE)
	$(RM) bootloader/_build-$(BOARD)_nrf52832//$(BOARD)_nrf52832_bootloader-*-nosd.hex
	$(MAKE) -C bootloader/ BOARD=$(BOARD)_nrf52832 all genhex
	$(PYTHON) tools/hexmerge.py \
		bootloader/_build-$(BOARD)_nrf52832/$(BOARD)_nrf52832_bootloader-*-nosd.hex \
		bootloader/lib/softdevice/s132_nrf52_6.1.1/s132_nrf52_6.1.1_softdevice.hex \
		-o build-$(BOARD)/bootloader.hex
	$(PYTHON) tools/hex2c.py build-$(BOARD)/bootloader.hex > \
		reloader/src/boards/$(BOARD)/bootloader.h
	$(PYTHON) -m nordicsemi dfu genpkg \
		--bootloader bootloader/_build-$(BOARD)_nrf52832//$(BOARD)_nrf52832_bootloader-*-nosd.hex \
		--softdevice bootloader/lib/softdevice/s132_nrf52_6.1.1/s132_nrf52_6.1.1_softdevice.hex \
		build-$(BOARD)/bootloader-daflasher.zip

reloader: bootloader build-$(BOARD_SAFE)
	$(MAKE) -C reloader/ BOARD=$(BOARD)
	cp reloader/build-$(BOARD)/reloader*.zip build-$(BOARD)

softdevice:
	micropython/ports/nrf/drivers/bluetooth/download_ble_stack.sh

wasp/boards/$(BOARD_SAFE)/watch.py : wasp/boards/$(BOARD_SAFE)/watch.py.in
	(cd wasp; ../tools/preprocess.py boards/$(BOARD)/watch.py.in > boards/$(BOARD)/watch.py) \
		|| ($(RM) wasp/boards/$(BOARD)/watch.py; false)

micropython/mpy-cross/mpy-cross:
	$(MAKE) -C micropython/mpy-cross \
		CWARN="-Wall -Wno-error"
		# ^ Disable some Werrors from GCC>=13, specifically
		#     - dangling-pointer
		#     - enum-int-mismatch
		#   TODO update micropython and remove.
		#   https://github.com/wasp-os/wasp-os/issues/493

micropython: build-$(BOARD_SAFE) wasp/boards/manifest_user_apps.py wasp/boards/$(BOARD_SAFE)/watch.py micropython/mpy-cross/mpy-cross
	$(RM) micropython/ports/nrf/build-$(BOARD)-s132/frozen_content.c
	$(MAKE) -C micropython/ports/nrf \
		BOARD=$(BOARD) SD=s132 \
		MICROPY_VFS_LFS2=1 \
		FROZEN_MANIFEST=$(CURDIR)/wasp/boards/$(BOARD)/manifest.py \
		USER_C_MODULES=$(CURDIR)/wasp/modules \
		COPT="-Wno-error"
		# ^ Disable some Werrors from GCC>=13, specifically
		#     - dangling-pointer
		#     - enum-int-mismatch
		#   TODO update micropython and remove.
		#   https://github.com/wasp-os/wasp-os/issues/493
	$(PYTHON) -m nordicsemi dfu genpkg \
		--dev-type 0x0052 \
		--application micropython/ports/nrf/build-$(BOARD)-s132/firmware.hex \
		build-$(BOARD)/micropython.zip

wasp/boards/manifest_user_apps.py: wasp.toml
	$(RM) -r \
		wasp/apps/user \
		wasp/boards/manifest_user_apps.py \
		wasp/appregistry.py
	mkdir -p wasp/apps/user
	$(PYTHON) tools/configure_wasp_apps.py wasp.toml

build-$(BOARD_SAFE):
	mkdir -p build-$(BOARD)

dfu:
	$(PYTHON) -m nordicsemi dfu serial --package micropython.zip --port /dev/ttyACM0

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

apps/%.mpy: apps/%.py micropython/mpy-cross/mpy-cross
	./micropython/mpy-cross/mpy-cross -mno-unicode -march=armv7m $<
APPS_PY=$(wildcard apps/*.py)
APPS_MPY=$(APPS_PY:%.py=%.mpy)
.PHONY: apps
apps: $(APPS_MPY)

docs: wasp/boards/manifest_user_apps.py
	$(RM) -rf docs/build/html/*
	$(MAKE) -C docs html
	touch docs/build/html/.nojekyll

sim: wasp/boards/manifest_user_apps.py
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:wasp/boards/simulator:wasp \
	$(PYTHON) -i wasp/boards/simulator/main.py

ifeq ("$(origin K)", "command line")
  PYTEST_RESTRICT = -k '$(K)'
endif

check: wasp/boards/manifest_user_apps.py
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:wasp/boards/simulator:wasp:wasp/apps/system \
	$(PYTEST) -v -W ignore $(PYTEST_RESTRICT) wasp/boards/simulator


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
	(cd ..; zip -9r $(DIST).zip $(notdir $(DIST)))

build-docker-image:
	docker compose \
	    --file ./tools/docker/docker-compose-build.yml \
	    build \
	        --pull

push-docker-image:
	docker compose \
	    --file ./tools/docker/docker-compose-build.yml \
	    push

run-docker-image:
	docker run \
	    --rm \
	    --volume=$$(pwd):/project/ \
	    --volume=/run/dbus:/run/dbus:ro \
	    --user=$$(id -u):$$(id -g) \
	    --userns=host \
	    --net=host \
	    --hostname="wasp-os-dev" \
	    --name="wasp-os-dev" \
	    --init \
	    --interactive \
	    --tty \
	    --entrypoint="" \
	    wasp-os/wasp-os-dev:0.1.0 \
	        bash
