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
aptget_update || aptget_update retry || aptget_update retry

set -e

sudo apt-get -qq install python3-tk libffi-dev libjpeg-turbo-progs libopenjp2-7-dev\
                         cmake

pip install --upgrade pip
PYTHONOPTIMIZE=0 pip install cffi
echo "PYR1"
pip install pyroma
echo "PYR2"
pip install setuptools==49.0.0
