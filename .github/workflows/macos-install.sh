#!/bin/bash

set -e

brew install libtiff libjpeg openjpeg libimagequant webp little-cms2

PYTHONOPTIMIZE=0 pip install cffi
pip install coverage
pip install olefile
pip install -U pytest
pip install -U pytest-cov
pip install pyroma

# extra test images
pushd depends && ./install_imagequant.sh && popd
