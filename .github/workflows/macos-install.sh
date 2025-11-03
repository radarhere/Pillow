#!/bin/bash

set -e

brew install \
    jpeg-turbo
brew uninstall freetype2 ant cairo fontconfig gradle harfbuzz kotlin maven openjdk selenium-server
export PKG_CONFIG_PATH="/usr/local/opt/openblas/lib/pkgconfig"

python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install ipython
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma

python3 -m pip install numpy
# optional test dependency, only install if there's a binary package.
# fails on beta 3.14 and PyPy
python3 -m pip install --only-binary=:all: pyarrow || true

# libavif
pushd depends && ./install_libavif.sh && popd

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
