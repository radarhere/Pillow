#!/bin/bash

set -e

if [[ "$ImageOS" == "macos13" ]]; then
    brew uninstall gradle maven
fi
brew install \
    jpeg-turbo \
    libtiff

python3 -m pip install coverage
