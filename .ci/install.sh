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
    sudo apt-get -qq install libfreetype6-dev liblcms2-dev python3-tk\
                             ghostscript libjpeg-turbo8-dev libopenjp2-7-dev\
                             cmake meson imagemagick libharfbuzz-dev libfribidi-dev\
                             sway wl-clipboard libopenblas-dev zlib1g-dev
fi

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade wheel
python3 -m pip install coverage
python3 -m pip install defusedxml
python3 -m pip install ipython
python3 -m pip install olefile
python3 -m pip install -U pytest
python3 -m pip install -U pytest-cov
python3 -m pip install -U pytest-timeout
python3 -m pip install pyroma
