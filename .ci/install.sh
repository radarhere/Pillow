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

sudo apt-get -qq install python3-tk\
                         libjpeg-turbo8-dev\
                         cmake meson\
                         sway wl-clipboard libopenblas-dev nasm

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade wheel
python3 -m pip install coverage
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma

echo "torchstart"
pushd depends && ./install_jpegxl.sh && popd
echo "torchend"

# extra test images
pushd depends && ./install_extra_test_images.sh && popd
