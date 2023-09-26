# NOTE: The officially tested toolchain is the one mentioned at
# https://wasp-os.readthedocs.io/en/latest/install.html#install-prerequisites
# So let's not add a flake.lock unless we test (and maintain) this thoroughly too.
{
  description = "A MicroPython based development environment for smart watches";
  outputs = { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSupportedSystems = nixpkgs.lib.genAttrs supportedSystems;
    in {
      devShells = forAllSupportedSystems (system: {
        default = import ./shell.nix { pkgs = nixpkgs.legacyPackages."${system}"; };
      });
    };
}
