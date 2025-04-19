# Software version pinning
FROM ubuntu:24.04
# Workaround: Newly introduced `ubuntu` user in ubuntu:24.04 causes UID/GID
# mapping issues when adding custom user
RUN touch /var/mail/ubuntu && \
    chown ubuntu /var/mail/ubuntu && \
    userdel --remove ubuntu

# Version info.
# `ARG DOCKER_IMG_VER=...` passed in via Docker Compose

# Main ("payload") software
ARG PAYLOAD=wasp-os-dev

# Docker image labels
LABEL maintainer="Wasp OS"
LABEL name="${PAYLOAD}"
LABEL description="Wasp OS developer environment"
LABEL version=${DOCKER_IMG_VER}

# Version info. (visible at run time from within Docker container)
ENV DOCKER_IMG_VER=${DOCKER_IMG_VER}

# Install base/support software
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --assume-yes --no-install-recommends \
        binutils-arm-none-eabi \
        bluez \
        build-essential \
        dbus \
        # TODO: Do version pinning?
        gcc \
        gcc-arm-none-eabi \
        gir1.2-gtk-4.0 \
        git \
        graphviz \
        libcairo2-dev \
        libgirepository-2.0-dev \
        libnewlib-arm-none-eabi \
        libsdl2-2.0.0 \
        make \
        pkg-config \
        python-is-python3 \
        python3 \
        python3-dev \
        python3-pil \
        python3-pip \
        python3-recommonmark \
        python3-sphinx \
        python3-venv \
        sphinx \
        unzip \
        wget \
    && \
    rm --recursive --force /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/python/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
COPY ./wasp/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir \
        --requirement /tmp/requirements.txt

# Install main ("payload") software
# None; Python scripts are provided through volumes at run time.

# Switch to non-root user
RUN groupadd ${PAYLOAD} && \
    useradd --no-log-init --gid ${PAYLOAD} ${PAYLOAD}
USER ${PAYLOAD}

# Set up working dir. and add to `$PATH` to ease project script exec.
WORKDIR /project/
ENV PATH="/project:$PATH"

# Execute main ("payload") software by default
ENTRYPOINT ["make"]
CMD ["--help"]
