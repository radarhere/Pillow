#!/bin/bash

set -e

python3 -c "from PIL import Image"

python3 -bb -m pytest -s -vv -x -W always --numprocesses=logical --dist=worksteal --cov PIL --cov Tests --cov-report term --cov-report xml Tests/test_image_quantize.py
