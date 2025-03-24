{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs.buildPackages; [
      # Node.js and npm for the Svelte frontend
      nodejs_20
      nodePackages.npm
    ];

    # Shell hook to set up the environment
    shellHook = ''
      echo "Node.js frontend development environment loaded"
      echo "Run 'npm install' to install dependencies (including Vite)"
      echo "Run 'npm run dev' to start the development server"

      # Create a .npmrc file to use npm for package management
      if [ ! -f .npmrc ]; then
        echo "Creating .npmrc file"
        echo "prefer-offline=true" > .npmrc
      fi
    '';
  }
