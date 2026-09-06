#!/bin/bash

set -e

python3 -m coverage erase
make clean

export CC="clang -fsanitize=undefined -fno-sanitize-recover=undefined"
export CXX="clang++ -fsanitize=undefined -fno-sanitize-recover=undefined"
export LDFLAGS="-fsanitize=undefined"
make install-coverage
