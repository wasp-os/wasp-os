FROM ubuntu:focal

ARG uid
ARG gid

RUN set -xe; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y \
      wget git build-essential pkg-config libsdl2-2.0.0 python3-click \
      python3-numpy python3-pexpect python3-pil python3-pip python3-pydbus \
      libcairo2-dev python3-serial unzip python3-sphinx graphviz \
      python3-recommonmark python3-pytest \
    ; \
    pip3 install cbor pysdl2 pygobject cryptography;

RUN set -xe; \
    wget --progress=dot:mega -O - https://developer.arm.com/-/media/Files/downloads/gnu-rm/10-2020q4/gcc-arm-none-eabi-10-2020-q4-major-x86_64-linux.tar.bz2 | tar xjf - -C /opt

RUN set -xe; \
    addgroup --gid $gid user; \
    adduser --gecos "" --disabled-password --uid $uid --gid $gid user;

COPY setup-env.sh /etc/profile.d/setup-env.sh
