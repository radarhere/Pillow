#!/bin/bash

./download-and-extract.sh libjxl-0.11.1 https://github.com/libjxl/libjxl/archive/refs/tags/v0.11.1.tar.gz

pushd libjxl-0.11.1

echo "torch1"

mkdir build
cd build
export CMAKE_INSTALL_PREFIX=/usr/local
export CMAKE_INSTALL_RPATH=/usr/local/lib
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF ..
cmake --build . -- -j4
echo "torch2"

sudo cmake --install .

popd

sudo ldconfig
