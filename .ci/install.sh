#!/bin/bash

aptget_update()
{
    if [ ! -z $1 ]; then
        echo ""
        echo "Retrying apt-get update..."
        echo ""
    fi
    output=`sudo apt-get update 2>&1`
    echo "$output"
    if [[ $output == *[WE]:\ * ]]; then
        return 1
    fi
}
if [[ $(uname) != CYGWIN* ]]; then
    aptget_update || aptget_update retry || aptget_update retry
fi

set -e

if [[ $(uname) != CYGWIN* ]]; then
    sudo apt-get -qq install python3-tk\
                             zlib1g-dev\
                             cmake meson
    sudo apt-get remove libjpeg-dev libjpeg-turbo8-dev libjpeg8-dev
    echo "torch"
    sudo apt list --installed
fi

git clone https://github.com/mozilla/mozjpeg.git
(cd mozjpeg \
    && git checkout v4.1.1 \
    && mkdir build \
    && cd build \
    && sudo cmake -G"Unix Makefiles" -D CMAKE_INSTALL_PREFIX=/usr/local ../ \
    && sudo make install)
sudo ldconfig

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade wheel
python3 -m pip install coverage
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma

if [[ $(uname) != CYGWIN* ]]; then
    # Pyroma uses non-isolated build and fails with old setuptools
    if [[ $GHA_PYTHON_VERSION == 3.9 ]]; then
        # To match pyproject.toml
        python3 -m pip install "setuptools>=67.8"
    fi

    # extra test images
    pushd depends && ./install_extra_test_images.sh && popd
else
    cd depends && ./install_extra_test_images.sh && cd ..
fi
