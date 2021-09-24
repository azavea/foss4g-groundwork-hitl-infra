with import <nixpkgs> {};

{ pkgs ? import <nixpkgs> {} }:
    let
	  python = python39.withPackages(ps: with ps; [ requests black ]);
	in
		pkgs.mkShell {
		name = "copy-campaigns";
		buildInputs = [ python ];
	}
