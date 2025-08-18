#!/bin/bash

set -e

python3 -c "from PIL import Image"

python3 -bb -m pytest -s -vv -W always Tests/test_file_jxl_animated.py
