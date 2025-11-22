#!/bin/bash

./download-and-extract.sh libjxl-0.9.4 https://github.com/libjxl/libjxl/archive/refs/tags/v0.9.4.tar.gz

pushd libjxl-0.9.4

echo "torch1"
./deps.sh
echo "torch2"

mkdir build
cd build
export CMAKE_INSTALL_PREFIX=/usr/local
export CMAKE_INSTALL_RPATH=/usr/local/lib
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF ..
cmake --build . -- -j4

sudo cmake --install .

popd

sudo ldconfig
