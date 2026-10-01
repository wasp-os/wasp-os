{ pkgs ? import <nixpkgs> {} }:

let
  # wasptool and ota-dfu only work on linux, and their dependencies prevent the
  # shell to evaluate on darwin
  ifLinux = pkgs.lib.optionals pkgs.stdenv.isLinux;

in pkgs.mkShell {
  buildInputs = ifLinux [
    pkgs.gobject-introspection
  ];
  nativeBuildInputs = [
    # Mirrors pyproject.toml (this shell uses nixpkgs' Python packages
    # rather than uv)
    (pkgs.python3.withPackages (pp: with pp; [
      # Firmware build
      adafruit-nrfutil
      cbor
      click
      cryptography
      intelhex

      # Simulator, tests and the Bluetooth tools
      dbus-python
      numpy
      pexpect
      pillow
      pygobject3
      pysdl2

      pytest

      # Docs
      sphinx
    ] ++ ifLinux [
      bluepy
    ]))
    pkgs.gcc-arm-embedded-11
    pkgs.graphviz
  ] ++ ifLinux [
    pkgs.bluez
  ];
}
