#!/bin/bash

set -e

python3 -c "from PIL import Image"

python3 -bb -m pytest -s -vv -x -W always Tests/test_image_access.py
