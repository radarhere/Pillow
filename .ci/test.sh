#!/bin/bash

set -e

echo "TORCH"
python -c "from PIL import _imaging"
echo "TORCH2"

# Docs
if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ] && [ "$TRAVIS_CPU_ARCH" == "amd64" ]; then
    make doccheck
fi
