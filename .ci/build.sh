#!/bin/bash

set -e

python3 -m coverage erase
make clean
python3 -m pip wheel .
