{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs.buildPackages; [
      # Use consistent Python version (3.12)
      python312Packages.pymongo
      python312Packages.pydantic
      python312Packages.fastapi
      python312Packages.python-dotenv
      python312Packages.uvicorn
      python312Packages.fastapi-cli
    ];
  }
