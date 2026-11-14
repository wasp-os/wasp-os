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
        libdbus-1-dev \
        libgirepository-2.0-dev \
        libnewlib-arm-none-eabi \
        make \
        pkg-config \
        python-is-python3 \
        python3 \
        python3-dev \
        unzip \
        wget \
    && \
    rm --recursive --force /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED=1
# Python tooling: uv installs the interpreter and all dependency groups into a
# venv outside /project (which is a volume mounted at run time).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_PROJECT_ENVIRONMENT=/opt/python/venv \
    UV_PYTHON_INSTALL_DIR=/opt/python/interpreters \
    UV_LINK_MODE=copy
COPY ./pyproject.toml ./uv.lock ./.python-version /tmp/wasp-os/
RUN cd /tmp/wasp-os && uv sync --locked --all-groups --no-cache && \
    chmod -R a+rX /opt/python
ENV VIRTUAL_ENV=/opt/python/venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

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
