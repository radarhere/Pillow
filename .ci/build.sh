#!/bin/bash

set -e

if [ $(uname) == "Darwin" ]; then
    export CPPFLAGS="-I/usr/local/miniconda/include";
fi
make clean
make install
