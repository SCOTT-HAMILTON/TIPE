{ pkgs ? import <nixpkgs> {} }:

let
  localShamilton = import /home/scott/GIT/nur-packages/default.nix {
    localUsage = true;
    nixosVersion = "master";
  };
  customPython = pkgs.python3.buildEnv.override {
    extraLibs = with pkgs.python3Packages; [
      numpy pandas matplotlib black
      localShamilton.phidget22
    ];
  };
in

pkgs.mkShell {
  buildInputs = [ customPython localShamilton.phidget22 localShamilton.libphidget ];
  shellHook = ''
    echo ${localShamilton.libphidget}/lib
    run(){
      sudo LD_LIBRARY_PATH="${localShamilton.libphidget}/lib" ${customPython}/bin/python3 run.py
    }
  '';
}

