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

if [[ $(uname) != CYGWIN* ]]; then
    python3 -m pip install numpy

    # PyQt6 doesn't support PyPy3
    if [[ $GHA_PYTHON_VERSION == 3.* ]]; then
        # TODO Update condition when pyqt6 supports free-threading
        if ! [[ "$PYTHON_GIL" == "0" ]]; then python3 -m pip install pyqt6 ; fi
    fi

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
