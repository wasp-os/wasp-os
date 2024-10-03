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
    (pkgs.python3.withPackages (pp: with pp; [
      cbor
      click
      cryptography
      dbus-python
      numpy
      pexpect
      pillow
      pygobject3
      pysdl2
      pyserial
      tomli

      pytest

      # Docs
      recommonmark
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
