#!/bin/bash

set -e

brew bundle --file=.github/workflows/Brewfile
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"

python3 -m pip install coverage
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
