{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };
  outputs = inputs @ {
    self,
    nixpkgs,
    flake-parts,
    ...
  }:
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux"];
      perSystem = {
        pkgs,
        lib,
        ...
      }: let
        python = pkgs.python3;

        remoteProjectPath = "~/projects/wcwp";
        remoteService = "wcwp.service";
        healthCheckUrl = "https://wcwp.dunderrrrrr.se/status";

        deployScript = pkgs.writeShellScriptBin "deploy" ''
          ssh -t hetzner-vps "cd ${remoteProjectPath} && git pull && sudo systemctl restart ${remoteService}"

          echo "Waiting for service to start..."
          sleep 2

          echo "Checking health endpoint..."
          response=$(curl -s ${healthCheckUrl})
          if [ "$response" = "ok" ]; then
            echo "✓ Deployment successful! Service is healthy."
          else
            echo "✗ Health check failed! Expected 'ok', got: $response"
            exit 1
          fi
        '';
      in {
        packages.deploy = deployScript;

        apps.deploy = {
          type = "app";
          program = "${deployScript}/bin/deploy";
        };

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.uv
            pkgs.ruff
            python
            (pkgs.writeShellScriptBin "run-server" ''
              python run.py
            '')
            deployScript
          ];
          shellHook = ''
            uv venv --clear
            source .venv/bin/activate
            uv pip sync requirements.txt
            pre-commit install --overwrite
            set -a
            source .env 2> /dev/null
          '';
        };
      };
    };
}
