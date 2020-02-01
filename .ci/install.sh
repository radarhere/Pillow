#!/bin/bash

set -e

sudo apt-get update
sudo apt-get -qq install liblcms2-dev python3-tk\
                         libffi-dev libjpeg-turbo-progs libopenjp2-7-dev\
                         cmake imagemagick libharfbuzz-dev libfribidi-dev

PYTHONOPTIMIZE=0 pip install cffi
pip install coverage
pip install olefile
pip install -U pytest
pip install -U pytest-cov
pip install pyroma

# docs only on Python 3.8
if [ "$TRAVIS_PYTHON_VERSION" == "3.8" ]; then pip install -r requirements.txt ; fi

# libimagequant
pushd depends && ./install_imagequant.sh && popd
