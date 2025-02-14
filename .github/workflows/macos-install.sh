#!/bin/bash

set -e

python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install ipython
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma
python3 -m pip install numpy

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
