#!/bin/bash

aptget_update()
{
    if [ -n "$1" ]; then
        echo ""
        echo "Retrying apt-get update..."
        echo ""
    fi
    output=$(sudo apt-get update 2>&1)
    echo "$output"
    if [[ $output == *[WE]:\ * ]]; then
        return 1
    fi
}
aptget_update || aptget_update retry || aptget_update retry

set -e

sudo apt-get -qq install libfreetype6-dev liblcms2-dev libtiff-dev python3-tk\
                         libjpeg-turbo8-dev libjxl-dev libopenjp2-7-dev\
                         cmake\
                         sway wl-clipboard libopenblas-dev nasm

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade wheel
python3 -m pip install coverage
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
