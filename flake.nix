{
  description = "SageAsk CLI — post questions to Discord, check replies";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "sageask";
          version = "0.1.0";
          src = ./src;
          pyproject = true;
          nativeBuildInputs = with pkgs.python3Packages; [ setuptools ];
          propagatedBuildInputs = with pkgs.python3Packages; [
            python-dotenv
            requests
          ];
        };

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            (python3.withPackages (ps: [
              ps.python-dotenv
              ps.requests
            ]))
          ];
          SHELL = "bash";
          shellHook = ''
            export SAGEASK_DATA=$(pwd)
          '';
        };
      }
    );
}
