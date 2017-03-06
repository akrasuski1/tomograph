#!/usr/bin/env bash

rm -rf out
mkdir -p out/{scan,sino,reco}
python tomography.py "$1" out/sino/ out/scan/ out/reco/
