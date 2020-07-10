#!/bin/bash

set -e

echo "TORCH"
python -m pytest -v -x -W always --cov PIL --cov Tests --cov-report term Tests
echo "TORCH2"

# Docs
if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ] && [ "$TRAVIS_CPU_ARCH" == "amd64" ]; then
    make doccheck
fi
